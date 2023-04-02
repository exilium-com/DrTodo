import typer
import rich
import rich.markdown
from rich_display import console


app = typer.Typer()


@app.command()
def mdfiles():
    md = rich.markdown.Markdown("""
Test

---
Test 2
**WORKS**
""")
    console.print(md)


@app.command()
def settings():
    print("settings")


if __name__ == "__main__":
    app()
