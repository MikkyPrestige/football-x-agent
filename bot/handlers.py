"""Telegram command handlers."""
from datetime import datetime, timedelta
from sqlalchemy import desc
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.database import SessionLocal
from core.models import Draft, Tweet, Rule, SourceHealth
from bot.keyboard import copy_buttons

# ---------- start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config.settings import ADMIN_CHAT_ID
    if str(update.effective_chat.id) != ADMIN_CHAT_ID:
        await update.message.reply_text("🚫 Unauthorized.")
        return
    await update.message.reply_text(
        "⚽ Welcome to your Football Twitter Agent!\n\n"
        "I'll push live match events and keep a queue of normal drafts for you to review.\n\n"
        "Commands:\n"
        "/queue - View pending normal drafts\n"
        "/posted <draft_id> - Mark a draft as posted and link a tweet ID\n"
        "/metrics <tweet_id> <likes> <retweets> <replies> <impressions> - Enter manual metrics\n"
        "/stats - Top & bottom tweets\n"
        "/rules - View / approve style rules\n"
        "/addrule <text> - Add a manual rule\n"
        "/source_status - Check news source health\n"
        "/backup - Backup database to Telegram"
    )

# ---------- queue ----------
async def queue_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config.settings import ADMIN_CHAT_ID
    if str(update.effective_chat.id) != ADMIN_CHAT_ID:
        await update.message.reply_text("🚫 Unauthorized.")
        return
    with SessionLocal() as session:
        drafts = session.query(Draft).filter(
            Draft.status == "pending",
            Draft.content_type == "normal"
        ).order_by(Draft.created_at.desc()).all()

    if not drafts:
        await update.message.reply_text("📭 No pending normal drafts. Check back later!")
        return

    for draft in drafts:
        variants = draft.text_variants
        header = f"📰 Draft #{draft.id} — {draft.persona} mode"
        msg = header + "\n\n" + "\n\n".join(
            f"**V{i+1}:** {v}" for i, v in enumerate(variants)
        )
        await update.message.reply_text(
            msg,
            reply_markup=copy_buttons(draft.id, variants),
            parse_mode="Markdown"
        )

# ---------- posted ----------
async def posted(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config.settings import ADMIN_CHAT_ID
    if str(update.effective_chat.id) != ADMIN_CHAT_ID:
        await update.message.reply_text("🚫 Unauthorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /posted <draft_id> [tweet_url_or_id]")
        return

    draft_id = int(context.args[0])
    tweet_ref = context.args[1] if len(context.args) > 1 else f"manual_{draft_id}"

    with SessionLocal() as session:
        draft = session.get(Draft, draft_id)
        if not draft:
            await update.message.reply_text("Draft not found.")
            return

        tweet = Tweet(
            id=tweet_ref,
            draft_id=draft.id,
            text=draft.text_variants[0],
            posted_at=datetime.utcnow(),
            likes=0,
            retweets=0,
            replies=0,
            impressions=0,
        )
        session.add(tweet)
        draft.status = "posted"
        draft.selected_variant = 0
        session.commit()

    await update.message.reply_text(
        f"✅ Draft #{draft_id} marked as posted and linked to tweet `{tweet_ref}`.\n"
        "Later, use `/metrics {tweet_ref} <likes> <retweets> <replies> <impressions>` to add engagement."
    )

# ---------- metrics ----------
async def metrics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config.settings import ADMIN_CHAT_ID
    if str(update.effective_chat.id) != ADMIN_CHAT_ID:
        await update.message.reply_text("🚫 Unauthorized.")
        return
    if len(context.args) != 5:
        await update.message.reply_text("Usage: /metrics <tweet_ref> <likes> <retweets> <replies> <impressions>")
        return

    tweet_ref = context.args[0]
    likes, retweets, replies, impressions = map(int, context.args[1:])

    with SessionLocal() as session:
        tweet = session.get(Tweet, tweet_ref)
        if not tweet:
            await update.message.reply_text("Tweet not found.")
            return
        tweet.likes = likes
        tweet.retweets = retweets
        tweet.replies = replies
        tweet.impressions = impressions
        tweet.last_metrics_fetch = datetime.utcnow()
        session.commit()

    await update.message.reply_text(
        f"✅ Metrics updated for tweet `{tweet_ref}`: "
        f"❤️ {likes} 🔄 {retweets} 💬 {replies} 👀 {impressions}"
    )

# ---------- stats ----------
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config.settings import ADMIN_CHAT_ID
    if str(update.effective_chat.id) != ADMIN_CHAT_ID:
        await update.message.reply_text("🚫 Unauthorized.")
        return
    with SessionLocal() as session:
        cutoff = datetime.utcnow() - timedelta(days=7)
        tweets = session.query(Tweet).filter(
            Tweet.posted_at >= cutoff
        ).order_by(desc(Tweet.likes)).all()

    if not tweets:
        await update.message.reply_text("No tweets recorded in the last 7 days.")
        return

    top5 = tweets[:5]
    bottom3 = tweets[-3:] if len(tweets) >= 3 else []

    msg = "📊 **Tweet Performance (last 7 days)**\n\n"
    msg += "**Top 5 by Likes:**\n"
    for i, t in enumerate(top5, 1):
        msg += f"{i}. {t.text[:60]}...  ❤️ {t.likes} 🔄 {t.retweets} 💬 {t.replies}\n"

    if bottom3:
        msg += "\n**Bottom 3:**\n"
        for i, t in enumerate(bottom3, 1):
            msg += f"{i}. {t.text[:60]}...  ❤️ {t.likes} 🔄 {t.retweets} 💬 {t.replies}\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

# ---------- rules ----------
async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config.settings import ADMIN_CHAT_ID
    if str(update.effective_chat.id) != ADMIN_CHAT_ID:
        await update.message.reply_text("🚫 Unauthorized.")
        return
    with SessionLocal() as session:
        active_rules = session.query(Rule).filter_by(active=True).all()
        suggested = session.query(Rule).filter_by(active=False, source="auto").all()

    msg = "📋 **Active Rules:**\n"
    if active_rules:
        for r in active_rules:
            msg += f"✅ {r.rule_text}\n"
    else:
        msg += "No active rules. Use /addrule to add one.\n"

    if suggested:
        msg += "\n**Suggested Rules (Accept/Reject):**\n"
        for r in suggested:
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Accept", callback_data=f"acceptrule_{r.id}"),
                    InlineKeyboardButton("Reject", callback_data=f"rejectrule_{r.id}")
                ]
            ])
            await update.message.reply_text(f"🤖 {r.rule_text}\n", reply_markup=keyboard)

    await update.message.reply_text(msg, parse_mode="Markdown")

# ---------- addrule ----------
async def addrule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config.settings import ADMIN_CHAT_ID
    if str(update.effective_chat.id) != ADMIN_CHAT_ID:
        await update.message.reply_text("🚫 Unauthorized.")
        return
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Usage: /addrule <rule text>")
        return
    with SessionLocal() as session:
        rule = Rule(rule_text=text, source="manual", active=True)
        session.add(rule)
        session.commit()
    await update.message.reply_text(f"✅ Rule added and active: {text}")

# ---------- source_status ----------
async def source_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config.settings import ADMIN_CHAT_ID
    if str(update.effective_chat.id) != ADMIN_CHAT_ID:
        await update.message.reply_text("🚫 Unauthorized.")
        return
    with SessionLocal() as session:
        sources = session.query(SourceHealth).all()
    if not sources:
        await update.message.reply_text("No source health data yet.")
        return
    msg = "📡 **Source Status:**\n"
    for s in sources:
        icon = "🟢" if s.status == "UP" else "🔴"
        msg += f"{icon} {s.source_name} – last success: {s.last_success}\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

# ---------- backup ----------
async def backup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config.settings import ADMIN_CHAT_ID
    if str(update.effective_chat.id) != ADMIN_CHAT_ID:
        await update.message.reply_text("🚫 Unauthorized.")
        return
    from core.backup import daily_backup
    try:
        path = daily_backup()
        await update.message.reply_text(f"✅ Backup created and sent: {path}")
    except Exception as e:
        await update.message.reply_text(f"❌ Backup failed: {e}")

# ---------- button handler ----------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config.settings import ADMIN_CHAT_ID
    if str(update.effective_chat.id) != ADMIN_CHAT_ID:
        await update.message.reply_text("🚫 Unauthorized.")
        return
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("copy_"):
        _, draft_id, variant_idx = data.split("_")
        draft_id = int(draft_id)
        variant_idx = int(variant_idx)
        with SessionLocal() as session:
            draft = session.get(Draft, draft_id)
            if draft:
                await query.message.reply_text(
                    draft.text_variants[variant_idx]
                )
                await query.message.reply_text(
                    "📋 After posting, use: `/posted {}`".format(draft_id),
                    parse_mode="Markdown"
                )
            else:
                await query.message.reply_text("Draft not found.")

    elif data.startswith("acceptrule_"):
        rule_id = int(data.split("_")[1])
        with SessionLocal() as session:
            rule = session.get(Rule, rule_id)
            if rule:
                rule.active = True
                session.commit()
                await query.edit_message_text(f"✅ Rule accepted: {rule.rule_text}")

    elif data.startswith("rejectrule_"):
        rule_id = int(data.split("_")[1])
        with SessionLocal() as session:
            rule = session.get(Rule, rule_id)
            if rule:
                session.delete(rule)
                session.commit()
                await query.edit_message_text(f"❌ Rule rejected and removed.")
