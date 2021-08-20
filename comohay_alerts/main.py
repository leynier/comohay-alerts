from os import system

from github import Github
from postgrest_py.utils import sanitize_param
from supabase_py import create_client
from telegram import Bot
from typer import Typer, echo

from .scraper import get_scraper
from .settings import get_settings

app = Typer()


@app.command()
def install():
    echo("Installing dependencies ...")
    system("poetry install")


@app.command()
def tests():
    echo("Running tests ...")
    system(
        "poetry run flake8 . --count --show-source "
        + "--statistics --max-line-length=88 --extend-ignore=E203"
    )
    system("poetry run black . --check")
    system("poetry run isort . --profile=black")


@app.command()
def export():
    system("poetry export -f requirements.txt -o requirements.txt --without-hashes")


@app.command()
def run():
    settings = get_settings()
    bot = Bot(token=settings.telegram_bot_token)
    scraper = get_scraper()
    supabase = create_client(settings.supabase_url, settings.supabase_key)
    gh = Github(settings.github_access_token)
    repo = gh.get_repo("leynier/comohay-alerts")
    issue = repo.get_issue(1)
    searchs = [
        list(map(lambda item: item.strip(), line.split(",")))
        for line in issue.body.splitlines()
    ]
    for search in searchs:
        for word in search:
            items = scraper.get_items(word)
            items.sort(key=lambda x: x.date, reverse=True)
            for item in items:
                resp = (
                    supabase.table("urls")
                    .select("url")  # type: ignore
                    .eq("url", item.url)
                    .limit(1)
                    .execute()
                )
                if resp["status_code"] == 200 and not resp["data"]:
                    value = {"url": sanitize_param(item.url)}
                    supabase.table("urls").insert(value).execute()  # type: ignore
                    message = (
                        f"Titulo: {item.title}\n"
                        + f"Fecha: {item.date}\n"
                        + f"Precio: {item.price}\n"
                        + f"Lugar: {item.location}\n"
                        + f"Descripción: {item.description}\n\n"
                        + f"{item.url}"
                    )
                    echo(message)
                    echo("======================================")
                    bot.send_message(
                        text=message,
                        chat_id=settings.telegram_chat_id,
                    )
