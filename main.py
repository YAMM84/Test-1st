#!/usr/bin/env python3
import sys
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich import box
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from stock_analysis import StockFetcher, TechnicalAnalysis, FundamentalAnalysis, Portfolio, ReportGenerator
from stock_analysis.demo_data import generate_demo_history, get_demo_info

console = Console()


def make_table(title: str, data: dict, value_style: str = "cyan") -> Table:
    table = Table(title=title, box=box.ROUNDED, title_style="bold blue", border_style="blue")
    table.add_column("項目", style="dim", width=24)
    table.add_column("値", style=value_style)
    for k, v in data.items():
        table.add_row(str(k), str(v) if v != "N/A" else "[dim]N/A[/dim]")
    return table


def signal_color(value: str) -> str:
    positive = ["上昇", "買いシグナル", "買われすぎ"]
    negative = ["下降", "売りシグナル", "売られすぎ"]
    if value in positive:
        return f"[green]{value}[/green]"
    if value in negative:
        return f"[red]{value}[/red]"
    return f"[yellow]{value}[/yellow]"


@click.group()
def cli():
    """株式投資分析ツール - 株価データのテクニカル・ファンダメンタル分析"""
    pass


@cli.command()
@click.argument("ticker")
@click.option("--period", "-p", default="1y", help="取得期間 (1d/5d/1mo/3mo/6mo/1y/2y/5y)")
@click.option("--chart", "-c", is_flag=True, help="チャートを生成する")
@click.option("--output-dir", "-o", default="./charts", help="チャート保存先ディレクトリ")
def analyze(ticker: str, period: str, chart: bool, output_dir: str):
    """銘柄の総合分析を行う\n\n例: python main.py analyze AAPL --chart"""
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task = progress.add_task(f"[cyan]{ticker} のデータを取得中...", total=None)

        try:
            fetcher = StockFetcher(ticker)
            df = fetcher.get_history(period=period)
            info = fetcher.get_info()
            company_name = fetcher.get_company_name()
            current_price = fetcher.get_current_price()
        except ValueError as e:
            console.print(f"[red]エラー: {e}[/red]")
            sys.exit(1)

        progress.update(task, description=f"[cyan]テクニカル分析中...")
        ta = TechnicalAnalysis(df)
        signals = ta.get_signals()
        score, rating = ta.get_summary_score()

        progress.update(task, description=f"[cyan]ファンダメンタル分析中...")
        fa = FundamentalAnalysis(info)

    console.print()
    console.print(Panel(
        f"[bold white]{company_name}[/bold white]  [dim]({ticker.upper()})[/dim]\n"
        f"[bold cyan]現在値: {current_price:,.2f} {info.get('currency', '')}[/bold cyan]  "
        f"[dim]期間: {period}[/dim]",
        title="[bold blue]株式投資分析レポート[/bold blue]",
        border_style="blue",
    ))

    rating_color = {
        "強い買い": "bright_green", "買い": "green",
        "中立": "yellow", "売り": "red", "強い売り": "bright_red"
    }.get(rating, "white")
    console.print(f"\n  テクニカル総合評価: [bold {rating_color}]{rating}[/bold {rating_color}]  (スコア: {score}/6)\n")

    sig_table = Table(title="テクニカルシグナル", box=box.ROUNDED, title_style="bold yellow", border_style="yellow")
    sig_table.add_column("指標", style="dim", width=20)
    sig_table.add_column("値", width=14)
    sig_table.add_column("判断", width=16)
    sig_table.add_row("現在株価", f"{signals['price']:,.2f}", "")
    sig_table.add_row("SMA20", f"{signals['sma20']:,.2f}", "")
    sig_table.add_row("SMA50", f"{signals['sma50']:,.2f}", "")
    sig_table.add_row("SMA200", f"{signals['sma200']:,.2f}" if signals['sma200'] else "N/A", "")
    sig_table.add_row("RSI(14)", f"{signals['rsi']:.1f}", signal_color(signals['rsi_status']))
    sig_table.add_row("MACD", f"{signals['macd']:.3f}", signal_color(signals['macd_crossover']))
    sig_table.add_row("トレンド", "", signal_color(signals['trend']))
    sig_table.add_row(
        "ゴールデンクロス",
        "[green]あり[/green]" if signals['golden_cross'] else "[red]なし[/red]", ""
    )
    console.print(sig_table)

    overview = fa.get_overview()
    valuation = fa.get_valuation()
    profitability = fa.get_profitability()
    health = fa.get_financial_health()
    dividend = fa.get_dividend()

    console.print()
    console.print(Columns([
        make_table("バリュエーション", valuation, "bright_cyan"),
        make_table("収益性", profitability, "bright_green"),
    ]))

    console.print()
    console.print(Columns([
        make_table("財務健全性", health, "yellow"),
        make_table("配当情報", dividend, "magenta"),
    ]))

    fund_score, fund_reasons = fa.get_investment_rating()
    if fund_reasons:
        console.print()
        fund_color = "green" if fund_score >= 4 else "yellow" if fund_score >= 2 else "red"
        console.print(Panel(
            "\n".join(f"  {'✓' if '+' not in r else '✓'} {r}" for r in fund_reasons),
            title=f"[bold]ファンダメンタル評価 (スコア: [{fund_color}]{fund_score}[/{fund_color}]/8)[/bold]",
            border_style=fund_color,
        ))

    if chart:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task("[cyan]チャートを生成中...", total=None)
            reporter = ReportGenerator(ticker)
            chart_path = reporter.generate_chart(period=period, output_dir=output_dir)
        console.print(f"\n[green]チャートを保存しました:[/green] {chart_path}")


@cli.command()
@click.argument("ticker")
@click.option("--period", "-p", default="1y", help="取得期間")
def technical(ticker: str, period: str):
    """テクニカル分析のみ実行\n\n例: python main.py technical TSLA"""
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(f"[cyan]{ticker} のデータを取得中...", total=None)
        try:
            fetcher = StockFetcher(ticker)
            df = fetcher.get_history(period=period)
        except ValueError as e:
            console.print(f"[red]エラー: {e}[/red]")
            sys.exit(1)

    ta = TechnicalAnalysis(df)
    signals = ta.get_signals()
    score, rating = ta.get_summary_score()

    rating_color = {
        "強い買い": "bright_green", "買い": "green",
        "中立": "yellow", "売り": "red", "強い売り": "bright_red"
    }.get(rating, "white")

    console.print(Panel(
        f"[bold {rating_color}]{rating}[/bold {rating_color}]  (スコア: {score}/6)",
        title=f"[bold blue]{ticker.upper()} テクニカル分析[/bold blue]",
        border_style="blue",
    ))

    table = Table(box=box.ROUNDED, border_style="blue")
    table.add_column("指標", style="dim")
    table.add_column("値")
    table.add_column("判断")

    rows = [
        ("現在株価", f"{signals['price']:,.2f}", ""),
        ("SMA20", f"{signals['sma20']:,.2f}", ""),
        ("SMA50", f"{signals['sma50']:,.2f}", ""),
        ("RSI(14)", f"{signals['rsi']:.1f}", signal_color(signals['rsi_status'])),
        ("MACDクロス", "", signal_color(signals['macd_crossover'])),
        ("トレンド", "", signal_color(signals['trend'])),
        ("BB上限", f"{signals['bb_upper']:,.2f}", ""),
        ("BB下限", f"{signals['bb_lower']:,.2f}", ""),
    ]
    for name, val, judge in rows:
        table.add_row(name, val, judge)

    console.print(table)


@cli.command()
@click.argument("ticker")
def fundamental(ticker: str):
    """ファンダメンタル分析のみ実行\n\n例: python main.py fundamental MSFT"""
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(f"[cyan]{ticker} のデータを取得中...", total=None)
        try:
            fetcher = StockFetcher(ticker)
            info = fetcher.get_info()
        except ValueError as e:
            console.print(f"[red]エラー: {e}[/red]")
            sys.exit(1)

    fa = FundamentalAnalysis(info)

    console.print(Panel(
        "\n".join(f"  [dim]{k}:[/dim] [white]{v}[/white]" for k, v in fa.get_overview().items()),
        title=f"[bold blue]{ticker.upper()} 企業概要[/bold blue]",
        border_style="blue",
    ))

    console.print()
    console.print(Columns([
        make_table("バリュエーション", fa.get_valuation(), "bright_cyan"),
        make_table("収益性", fa.get_profitability(), "bright_green"),
    ]))
    console.print()
    console.print(Columns([
        make_table("財務健全性", fa.get_financial_health(), "yellow"),
        make_table("成長性", fa.get_growth(), "magenta"),
    ]))
    console.print()
    console.print(make_table("配当情報", fa.get_dividend(), "bright_magenta"))


@cli.command()
@click.argument("ticker")
@click.option("--period", "-p", default="1y", help="取得期間")
@click.option("--output-dir", "-o", default="./charts", help="保存先ディレクトリ")
def chart(ticker: str, period: str, output_dir: str):
    """株価チャートを生成する\n\n例: python main.py chart GOOGL -p 6mo"""
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(f"[cyan]{ticker} のチャートを生成中...", total=None)
        reporter = ReportGenerator(ticker)
        try:
            chart_path = reporter.generate_chart(period=period, output_dir=output_dir)
        except ValueError as e:
            console.print(f"[red]エラー: {e}[/red]")
            sys.exit(1)

    console.print(f"[green]チャートを保存しました:[/green] {chart_path}")


@cli.group()
def portfolio():
    """ポートフォリオの管理"""
    pass


@portfolio.command("add")
@click.argument("ticker")
@click.argument("shares", type=float)
@click.argument("buy_price", type=float)
@click.option("--note", "-n", default="", help="メモ")
def portfolio_add(ticker: str, shares: float, buy_price: float, note: str):
    """銘柄をポートフォリオに追加\n\n例: python main.py portfolio add AAPL 10 150.00"""
    p = Portfolio()
    p.add(ticker, shares, buy_price, note)
    console.print(f"[green]{ticker.upper()} を追加しました ({shares}株 @ ${buy_price:,.2f})[/green]")


@portfolio.command("remove")
@click.argument("ticker")
def portfolio_remove(ticker: str):
    """銘柄をポートフォリオから削除\n\n例: python main.py portfolio remove AAPL"""
    p = Portfolio()
    if p.remove(ticker):
        console.print(f"[yellow]{ticker.upper()} を削除しました[/yellow]")
    else:
        console.print(f"[red]{ticker.upper()} はポートフォリオに存在しません[/red]")


@portfolio.command("show")
def portfolio_show():
    """ポートフォリオの損益一覧を表示\n\n例: python main.py portfolio show"""
    p = Portfolio()
    if p.is_empty():
        console.print("[yellow]ポートフォリオが空です。[/yellow]  python main.py portfolio add <TICKER> <株数> <購入価格>")
        return

    tickers = p.get_tickers()

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task("[cyan]現在株価を取得中...", total=None)
        current_prices = {}
        for t in tickers:
            try:
                current_prices[t] = StockFetcher(t).get_current_price()
            except Exception:
                current_prices[t] = None

    rows = p.get_summary(current_prices)

    table = Table(title="ポートフォリオ損益", box=box.ROUNDED, title_style="bold blue", border_style="blue")
    table.add_column("銘柄", style="bold")
    table.add_column("株数", justify="right")
    table.add_column("購入単価", justify="right", style="dim")
    table.add_column("現在値", justify="right")
    table.add_column("評価額", justify="right")
    table.add_column("損益", justify="right")
    table.add_column("損益率", justify="right")
    table.add_column("メモ", style="dim")

    total_cost = 0
    total_value = 0

    for row in rows:
        pnl_color = "green" if row["pnl"] >= 0 else "red"
        table.add_row(
            row["ticker"],
            f"{row['shares']:g}",
            f"${row['buy_price']:,.2f}",
            f"${row['current_price']:,.2f}",
            f"${row['value']:,.2f}",
            f"[{pnl_color}]{'+'if row['pnl']>=0 else ''}${row['pnl']:,.2f}[/{pnl_color}]",
            f"[{pnl_color}]{'+'if row['pnl_pct']>=0 else ''}{row['pnl_pct']:.2f}%[/{pnl_color}]",
            row["note"],
        )
        total_cost += row["cost"]
        total_value += row["value"]

    console.print(table)

    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
    color = "green" if total_pnl >= 0 else "red"
    console.print(
        f"\n  [bold]合計評価額:[/bold] [cyan]${total_value:,.2f}[/cyan]  "
        f"[bold]総損益:[/bold] [{color}]{'+'if total_pnl>=0 else ''}${total_pnl:,.2f}  "
        f"({'+'if total_pnl_pct>=0 else ''}{total_pnl_pct:.2f}%)[/{color}]"
    )


@cli.command()
@click.argument("tickers", nargs=-1, required=True)
def compare(tickers: tuple):
    """複数銘柄を比較する\n\n例: python main.py compare AAPL MSFT GOOGL"""
    results = []

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task = progress.add_task("[cyan]データ取得中...", total=None)
        for t in tickers:
            progress.update(task, description=f"[cyan]{t} を取得中...")
            try:
                fetcher = StockFetcher(t)
                df = fetcher.get_history(period="1y")
                info = fetcher.get_info()
                ta = TechnicalAnalysis(df)
                fa = FundamentalAnalysis(info)
                score, rating = ta.get_summary_score()
                fund_score, _ = fa.get_investment_rating()
                current = fetcher.get_current_price()
                valuation = fa.get_valuation()
                profitability = fa.get_profitability()
                results.append({
                    "ticker": t.upper(),
                    "name": fetcher.get_company_name()[:20],
                    "price": current,
                    "tech_rating": rating,
                    "tech_score": score,
                    "fund_score": fund_score,
                    "per": valuation.get("PER (株価収益率)", "N/A"),
                    "pbr": valuation.get("PBR (株価純資産倍率)", "N/A"),
                    "roe": profitability.get("ROE (自己資本利益率)", "N/A"),
                    "margin": profitability.get("純利益率", "N/A"),
                    "market_cap": valuation.get("時価総額", "N/A"),
                })
            except Exception as e:
                console.print(f"[red]{t}: {e}[/red]")

    table = Table(title="銘柄比較", box=box.ROUNDED, title_style="bold blue", border_style="blue")
    table.add_column("銘柄", style="bold")
    table.add_column("企業名", style="dim")
    table.add_column("現在値", justify="right")
    table.add_column("時価総額", justify="right")
    table.add_column("PER", justify="right")
    table.add_column("PBR", justify="right")
    table.add_column("ROE", justify="right")
    table.add_column("純利益率", justify="right")
    table.add_column("テクニカル", justify="center")
    table.add_column("ファンダ", justify="center")

    rating_colors = {
        "強い買い": "bright_green", "買い": "green",
        "中立": "yellow", "売り": "red", "強い売り": "bright_red"
    }

    for r in results:
        rc = rating_colors.get(r["tech_rating"], "white")
        table.add_row(
            r["ticker"],
            r["name"],
            f"${r['price']:,.2f}",
            str(r["market_cap"]),
            str(r["per"]),
            str(r["pbr"]),
            str(r["roe"]),
            str(r["margin"]),
            f"[{rc}]{r['tech_rating']}[/{rc}]",
            f"{r['fund_score']}/8",
        )

    console.print(table)


@cli.command()
@click.argument("ticker", default="AAPL")
@click.option("--chart", "-c", is_flag=True, help="チャートも生成する")
@click.option("--output-dir", "-o", default="./charts")
def demo(ticker: str, chart: bool, output_dir: str):
    """デモデータで分析機能を体験する (ネット不要)\n\n例: python main.py demo AAPL --chart"""
    console.print(Panel(
        "[yellow]デモモード: 生成データを使用しています (実際の株価ではありません)[/yellow]",
        border_style="yellow",
    ))

    df = generate_demo_history(ticker, days=365)
    info = get_demo_info(ticker)
    company_name = info.get("longName", ticker)
    current_price = float(df["Close"].iloc[-1])

    ta = TechnicalAnalysis(df)
    signals = ta.get_signals()
    score, rating = ta.get_summary_score()
    fa = FundamentalAnalysis(info)

    rating_color = {
        "強い買い": "bright_green", "買い": "green",
        "中立": "yellow", "売り": "red", "強い売り": "bright_red"
    }.get(rating, "white")

    console.print()
    console.print(Panel(
        f"[bold white]{company_name}[/bold white]  [dim]({ticker.upper()})[/dim]\n"
        f"[bold cyan]現在値: {current_price:,.2f} {info.get('currency', 'USD')}[/bold cyan]  "
        f"[dim][デモデータ][/dim]",
        title="[bold blue]株式投資分析レポート (デモ)[/bold blue]",
        border_style="blue",
    ))

    console.print(f"\n  テクニカル総合評価: [bold {rating_color}]{rating}[/bold {rating_color}]  (スコア: {score}/6)\n")

    sig_table = Table(title="テクニカルシグナル", box=box.ROUNDED, title_style="bold yellow", border_style="yellow")
    sig_table.add_column("指標", style="dim", width=20)
    sig_table.add_column("値", width=14)
    sig_table.add_column("判断", width=16)
    sig_table.add_row("現在株価", f"{signals['price']:,.2f}", "")
    sig_table.add_row("SMA20", f"{signals['sma20']:,.2f}", "")
    sig_table.add_row("SMA50", f"{signals['sma50']:,.2f}", "")
    sig_table.add_row("RSI(14)", f"{signals['rsi']:.1f}", signal_color(signals['rsi_status']))
    sig_table.add_row("MACD", f"{signals['macd']:.3f}", signal_color(signals['macd_crossover']))
    sig_table.add_row("トレンド", "", signal_color(signals['trend']))
    sig_table.add_row(
        "ゴールデンクロス",
        "[green]あり[/green]" if signals['golden_cross'] else "[red]なし[/red]", ""
    )
    console.print(sig_table)

    console.print()
    console.print(Columns([
        make_table("バリュエーション", fa.get_valuation(), "bright_cyan"),
        make_table("収益性", fa.get_profitability(), "bright_green"),
    ]))
    console.print()
    console.print(Columns([
        make_table("財務健全性", fa.get_financial_health(), "yellow"),
        make_table("配当情報", fa.get_dividend(), "magenta"),
    ]))

    fund_score, fund_reasons = fa.get_investment_rating()
    if fund_reasons:
        console.print()
        fund_color = "green" if fund_score >= 4 else "yellow" if fund_score >= 2 else "red"
        console.print(Panel(
            "\n".join(f"  ✓ {r}" for r in fund_reasons),
            title=f"[bold]ファンダメンタル評価 (スコア: [{fund_color}]{fund_score}[/{fund_color}]/8)[/bold]",
            border_style=fund_color,
        ))

    if chart:
        import matplotlib
        matplotlib.use("Agg")
        from stock_analysis.report import ReportGenerator as RG
        import os
        os.makedirs(output_dir, exist_ok=True)
        from datetime import datetime as dt
        from stock_analysis.report import ReportGenerator
        reporter = ReportGenerator.__new__(ReportGenerator)
        reporter.ticker = ticker.upper()
        chart_path = reporter.generate_chart.__func__(reporter, period="1y", output_dir=output_dir) \
            if False else _generate_demo_chart(ticker, df, output_dir)
        console.print(f"\n[green]チャートを保存しました:[/green] {chart_path}")


def _generate_demo_chart(ticker: str, df, output_dir: str) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    import os
    from datetime import datetime as dt

    ta = TechnicalAnalysis(df)
    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor("#0d1117")
    gs = gridspec.GridSpec(4, 1, height_ratios=[3, 1, 1, 1], hspace=0.05)
    axes = [fig.add_subplot(gs[i]) for i in range(4)]
    for ax in axes:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#8b949e")
        for spine in ax.spines.values():
            spine.set_color("#21262d")

    dates = df.index
    close = df["Close"]
    upper_bb, middle_bb, lower_bb = ta.bollinger_bands()
    sma20, sma50 = ta.sma(20), ta.sma(50)
    ax1, ax2, ax3, ax4 = axes

    ax1.plot(dates, close, color="#58a6ff", linewidth=1.5, label="Close")
    ax1.plot(dates, sma20, color="#f0883e", linewidth=1, linestyle="--", label="SMA20", alpha=0.8)
    ax1.plot(dates, sma50, color="#3fb950", linewidth=1, linestyle="--", label="SMA50", alpha=0.8)
    ax1.fill_between(dates, upper_bb, lower_bb, alpha=0.1, color="#58a6ff")
    ax1.plot(dates, upper_bb, color="#58a6ff", linewidth=0.5, alpha=0.5)
    ax1.plot(dates, lower_bb, color="#58a6ff", linewidth=0.5, alpha=0.5)
    ax1.set_ylabel("Price", color="#8b949e")
    ax1.legend(loc="upper left", facecolor="#161b22", edgecolor="#21262d", labelcolor="#c9d1d9", fontsize=8)
    ax1.set_title(f"{ticker.upper()} Stock Chart [DEMO]", color="#c9d1d9", fontsize=14, pad=10)

    colors = ["#3fb950" if c >= o else "#f85149" for c, o in zip(df["Close"], df["Open"])]
    ax2.bar(dates, df["Volume"], color=colors, alpha=0.7)
    ax2.set_ylabel("Volume", color="#8b949e")

    rsi = ta.rsi()
    ax3.plot(dates, rsi, color="#d2a8ff", linewidth=1.2)
    ax3.axhline(70, color="#f85149", linestyle="--", linewidth=0.8, alpha=0.7)
    ax3.axhline(30, color="#3fb950", linestyle="--", linewidth=0.8, alpha=0.7)
    ax3.fill_between(dates, rsi, 70, where=(rsi > 70), alpha=0.2, color="#f85149")
    ax3.fill_between(dates, rsi, 30, where=(rsi < 30), alpha=0.2, color="#3fb950")
    ax3.set_ylim(0, 100)
    ax3.set_ylabel("RSI", color="#8b949e")

    macd_line, signal_line, histogram = ta.macd()
    ax4.bar(dates, histogram, color=["#3fb950" if v >= 0 else "#f85149" for v in histogram], alpha=0.7)
    ax4.plot(dates, macd_line, color="#58a6ff", linewidth=1, label="MACD")
    ax4.plot(dates, signal_line, color="#f0883e", linewidth=1, label="Signal")
    ax4.axhline(0, color="#8b949e", linewidth=0.5)
    ax4.set_ylabel("MACD", color="#8b949e")
    ax4.legend(loc="upper left", facecolor="#161b22", edgecolor="#21262d", labelcolor="#c9d1d9", fontsize=7)

    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.setp(ax3.get_xticklabels(), visible=False)

    os.makedirs(output_dir, exist_ok=True)
    filename = f"{ticker.upper()}_demo_chart_{dt.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close()
    return filepath


if __name__ == "__main__":
    cli()
