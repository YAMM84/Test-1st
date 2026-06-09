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
from rich.rule import Rule

from stock_analysis import StockFetcher, TechnicalAnalysis, FundamentalAnalysis, Portfolio, ReportGenerator
from stock_analysis.demo_data import generate_demo_history, get_demo_info
from wealth_optimizer import (
    CompoundGrowthSimulator, STRATEGIES, StrategyAnalyzer, BillionaireRoadmap,
    MonteCarloEngine, EfficientFrontierOptimizer, CANDIDATE_UNIVERSE,
    StockScreener, ExecutionPlanner,
)
from wealth_optimizer.allocator import (
    get_allocation, get_age_based_allocation, recommend_profile, RISK_PROFILES,
)

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


@cli.group()
def wealth():
    """億万長者への最適化戦略ツール"""
    pass


@wealth.command("simulate")
@click.option("--capital", "-c", default=1_000_000, type=float, help="初期資金 (円)", show_default=True)
@click.option("--monthly", "-m", default=50_000, type=float, help="毎月積立額 (円)", show_default=True)
@click.option("--rate", "-r", default=7.0, type=float, help="年間リターン率 (%)", show_default=True)
@click.option("--years", "-y", default=30, type=int, help="シミュレーション年数", show_default=True)
@click.option("--target", "-t", default=100_000_000, type=float, help="目標資産額 (円)", show_default=True)
def wealth_simulate(capital: float, monthly: float, rate: float, years: int, target: float):
    """複利成長シミュレーション\n\n例: python main.py wealth simulate -c 2000000 -m 100000 -r 7"""
    sim = CompoundGrowthSimulator(capital, rate / 100, monthly)
    result = sim.simulate(years=years, target=target)

    target_label = f"{target/1_000_000:.0f}百万円" if target < 1_000_000_000 else f"{target/1_000_000_000:.1f}十億円"

    console.print()
    console.print(Panel(
        f"[bold white]初期資金:[/bold white] [cyan]{capital:,.0f}円[/cyan]  "
        f"[bold white]月次積立:[/bold white] [cyan]{monthly:,.0f}円[/cyan]  "
        f"[bold white]年率:[/bold white] [cyan]{rate}%[/cyan]  "
        f"[bold white]目標:[/bold white] [yellow]{target:,.0f}円[/yellow]",
        title="[bold blue]複利成長シミュレーター[/bold blue]",
        border_style="blue",
    ))

    if result.years_to_target:
        console.print(f"\n  [bold green]目標達成まで約 {result.years_to_target} 年![/bold green]\n")
    else:
        needed = sim.required_monthly_contribution(target, years)
        console.print(
            f"\n  [yellow]{years}年以内に目標未達。達成に必要な月積立:[/yellow] "
            f"[bold]{needed:,.0f}円/月[/bold]\n"
        )

    table = Table(title="年別資産推移", box=box.ROUNDED, title_style="bold yellow", border_style="yellow")
    table.add_column("年", justify="right", style="dim")
    table.add_column("資産残高", justify="right")
    table.add_column("累計投資額", justify="right", style="dim")
    table.add_column("運用益", justify="right")
    table.add_column("達成率", justify="right")

    for yr, val in result.year_by_year:
        contributed = capital + monthly * yr * 12
        growth = val - contributed
        rate_pct = val / target * 100
        color = "green" if val >= target else "cyan" if val >= target * 0.5 else "white"
        reached = " [bold green]★達成![/bold green]" if val >= target else ""
        table.add_row(
            f"{yr}年",
            f"[{color}]{val:,.0f}円[/{color}]{reached}",
            f"{contributed:,.0f}円",
            f"[green]+{growth:,.0f}円[/green]" if growth >= 0 else f"[red]{growth:,.0f}円[/red]",
            f"{rate_pct:.1f}%",
        )

    console.print(table)

    console.print(
        f"\n  [bold]最終資産:[/bold] [bold cyan]{result.final_value:,.0f}円[/bold cyan]  "
        f"[bold]累計投資:[/bold] {result.total_contributed:,.0f}円  "
        f"[bold]運用益:[/bold] [green]+{result.total_growth:,.0f}円[/green]  "
        f"[bold]倍率:[/bold] [yellow]{result.final_value/capital:.1f}倍[/yellow]"
    )


@wealth.command("strategies")
def wealth_strategies():
    """富の構築戦略を比較する\n\n例: python main.py wealth strategies"""
    analyzer = StrategyAnalyzer()
    ranked = analyzer.rank_by_sharpe()

    console.print()
    console.print(Panel(
        "各戦略の期待リターン・リスク・手間・必要資金を総合評価",
        title="[bold blue]富の構築戦略比較[/bold blue]",
        border_style="blue",
    ))

    table = Table(box=box.ROUNDED, title_style="bold yellow", border_style="yellow")
    table.add_column("戦略", style="bold", width=22)
    table.add_column("期待年率", justify="right")
    table.add_column("リスク", justify="right")
    table.add_column("シャープ比", justify="right")
    table.add_column("必要資金", justify="right", style="dim")
    table.add_column("月次工数", justify="right", style="dim")
    table.add_column("総合スコア", justify="center")

    return_colors = {True: "bright_green", False: "red"}
    for s in ranked:
        sharpe = analyzer.get_sharpe(s)
        score = analyzer.get_score(s)
        score_color = "bright_green" if score >= 7 else "green" if score >= 5 else "yellow"
        table.add_row(
            s.name_jp,
            f"[{'bright_green' if s.annual_return >= 0.10 else 'green' if s.annual_return >= 0.07 else 'yellow'}]{s.annual_return*100:.0f}%[/]",
            f"[{'red' if s.volatility >= 0.40 else 'yellow' if s.volatility >= 0.20 else 'green'}]{s.volatility*100:.0f}%[/]",
            f"{sharpe:.2f}",
            f"{s.required_capital:,.0f}円〜",
            f"{s.monthly_effort}h/月",
            f"[{score_color}]{score}/10[/{score_color}]",
        )

    console.print(table)
    console.print("\n[dim]シャープ比 = (期待リターン - 無リスク金利) / リスク（高いほど効率が良い）[/dim]\n")

    console.print(Rule("[bold yellow]推奨戦略の詳細[/bold yellow]"))
    best = ranked[0]
    console.print(Panel(
        f"[bold]{best.description}[/bold]\n\n"
        f"[bold green]メリット:[/bold green]\n" +
        "\n".join(f"  ✓ {p}" for p in best.pros) +
        f"\n\n[bold red]デメリット:[/bold red]\n" +
        "\n".join(f"  ✗ {c}" for c in best.cons) +
        f"\n\n[bold cyan]アクションステップ:[/bold cyan]\n" +
        "\n".join(f"  {i+1}. {a}" for i, a in enumerate(best.action_steps)),
        title=f"[bold]シャープ比最優秀: {best.name_jp}[/bold]",
        border_style="green",
    ))


@wealth.command("allocate")
@click.option("--age", "-a", default=30, type=int, help="年齢", show_default=True)
@click.option("--risk", "-r", default="medium", type=click.Choice(["low", "medium", "high"]), help="リスク許容度")
@click.option("--debt/--no-debt", default=False, help="高利息負債の有無")
@click.option("--capital", "-c", default=3_000_000, type=float, help="運用資金 (円)", show_default=True)
def wealth_allocate(age: int, risk: str, debt: bool, capital: float):
    """最適な資産配分を提案する\n\n例: python main.py wealth allocate --age 35 --risk high -c 5000000"""
    profile = recommend_profile(age, risk, debt)
    alloc = get_allocation(profile)
    profile_data = RISK_PROFILES[profile]

    console.print()
    console.print(Panel(
        f"[bold white]年齢:[/bold white] [cyan]{age}歳[/cyan]  "
        f"[bold white]リスク許容度:[/bold white] [cyan]{risk}[/cyan]  "
        f"[bold white]運用資金:[/bold white] [cyan]{capital:,.0f}円[/cyan]  "
        f"{'[bold red]高利息負債あり[/bold red]' if debt else '[green]負債なし[/green]'}",
        title="[bold blue]最適資産配分レコメンデーション[/bold blue]",
        border_style="blue",
    ))

    name_jp = profile_data["name_jp"]
    lc = profile_data["label_color"]
    console.print(f"\n  推奨プロファイル: [bold {lc}]{name_jp}[/bold {lc}]  "
                  f"期待年率 [cyan]{alloc.expected_return*100:.0f}%[/cyan]  "
                  f"想定ボラ [yellow]{alloc.expected_volatility*100:.0f}%[/yellow]\n")

    table = Table(title="推奨アセット配分", box=box.ROUNDED, title_style="bold yellow", border_style="yellow")
    table.add_column("アセットクラス", style="bold")
    table.add_column("配分比率", justify="right")
    table.add_column("投資額 (円)", justify="right")
    table.add_column("年間期待リターン", justify="right")

    for asset, pct in alloc.allocations.items():
        amount = capital * pct / 100
        yr_return = amount * alloc.expected_return * (pct / 100) * (100 / sum(alloc.allocations.values()))
        pct_color = "bright_green" if pct >= 30 else "green" if pct >= 15 else "dim"
        table.add_row(
            asset,
            f"[{pct_color}]{pct:.0f}%[/{pct_color}]",
            f"{amount:,.0f}円",
            f"+{amount * alloc.expected_return * pct / sum(alloc.allocations.values()) / 100:,.0f}円",
        )

    console.print(table)

    console.print()
    console.print(Panel(
        "\n".join(f"  • {note}" for note in alloc.notes),
        title="[bold]運用ガイドライン[/bold]",
        border_style="cyan",
    ))

    sim = CompoundGrowthSimulator(capital, alloc.expected_return, 0)
    result_10 = sim.simulate(years=10)
    result_20 = sim.simulate(years=20)
    result_30 = sim.simulate(years=30)
    console.print(
        f"\n  [bold]この配分での成長予測:[/bold]  "
        f"10年後 [cyan]{result_10.final_value:,.0f}円[/cyan]  "
        f"20年後 [cyan]{result_20.final_value:,.0f}円[/cyan]  "
        f"30年後 [cyan]{result_30.final_value:,.0f}円[/cyan]"
    )


@wealth.command("plan")
@click.option("--capital", "-c", default=0, type=float, help="現在の総資産 (円)", show_default=True)
@click.option("--monthly", "-m", default=50_000, type=float, help="毎月の積立可能額 (円)", show_default=True)
@click.option("--age", "-a", default=30, type=int, help="現在の年齢", show_default=True)
@click.option("--rate", "-r", default=7.0, type=float, help="想定年率リターン (%)", show_default=True)
def wealth_plan(capital: float, monthly: float, age: int, rate: float):
    """億万長者ロードマップを表示する\n\n例: python main.py wealth plan --capital 2000000 --monthly 80000 --age 28"""
    roadmap = BillionaireRoadmap(capital, monthly, rate / 100)
    milestones = roadmap.get_milestones()
    stats = roadmap.get_motivational_stats()
    years_to_1oku = roadmap.years_to_100m()

    console.print()
    console.print(Panel(
        f"[bold white]現在資産:[/bold white] [cyan]{capital:,.0f}円[/cyan]  "
        f"[bold white]月積立:[/bold white] [cyan]{monthly:,.0f}円[/cyan]  "
        f"[bold white]年齢:[/bold white] [cyan]{age}歳[/cyan]  "
        f"[bold white]想定年率:[/bold white] [cyan]{rate}%[/cyan]",
        title="[bold blue]億万長者ロードマップ[/bold blue]",
        border_style="blue",
    ))

    if years_to_1oku:
        reach_age = age + years_to_1oku
        console.print(
            f"\n  [bold bright_yellow]1億円達成予測: {years_to_1oku}年後 "
            f"({reach_age}歳頃)[/bold bright_yellow]\n"
        )
    else:
        console.print(
            f"\n  [yellow]現在の条件では60年以内に1億円未達。月積立増加か運用改善が必要。[/yellow]\n"
        )

    for i, milestone in enumerate(milestones):
        is_completed = capital >= milestone.target_jpy
        is_next = not is_completed and (i == 0 or capital >= milestones[i - 1].target_jpy)

        if is_completed:
            status = "[bold green]✓ 達成済み[/bold green]"
            border = "green"
        elif is_next:
            status = "[bold yellow]→ 次の目標[/bold yellow]"
            border = "yellow"
        else:
            status = "[dim]未達成[/dim]"
            border = "dim"

        progress_pct = min(100, capital / milestone.target_jpy * 100) if milestone.target_jpy > 0 else 0
        bar_len = 20
        filled = int(bar_len * progress_pct / 100)
        bar = f"[green]{'█' * filled}[/green][dim]{'░' * (bar_len - filled)}[/dim] {progress_pct:.0f}%"

        sim = CompoundGrowthSimulator(capital, rate / 100, monthly)
        m_result = sim.simulate(years=60, target=milestone.target_jpy)
        eta = f" → 約{m_result.years_to_target}年で到達" if m_result.years_to_target and not is_completed else ""

        actions_text = "\n".join(f"  {j+1}. {a}" for j, a in enumerate(milestone.key_actions))
        console.print(Panel(
            f"{status}{eta}\n"
            f"[dim]フェーズ:[/dim] {milestone.phase}  [dim]目安期間:[/dim] {milestone.years_estimate}\n"
            f"進捗: {bar}\n\n"
            f"[bold cyan]主要アクション:[/bold cyan]\n{actions_text}\n\n"
            f"[bold magenta]マインドセット:[/bold magenta] [italic]{milestone.mindset}[/italic]",
            title=f"[bold] Step {i+1}: {milestone.name} [{milestone.target_label}][/bold]",
            border_style=border,
        ))

    console.print()
    console.print(Rule("[bold yellow]資産成長シミュレーション[/bold yellow]"))

    sim_table = Table(box=box.ROUNDED, border_style="yellow")
    sim_table.add_column("時点", style="bold")
    sim_table.add_column("予測資産", justify="right")
    sim_table.add_column("年齢", justify="right", style="dim")
    sim_table.add_column("1億円まで", justify="right")

    checkpoints = [5, 10, 15, 20, 25, 30]
    for yr in checkpoints:
        sim = CompoundGrowthSimulator(capital, rate / 100, monthly)
        r = sim.simulate(years=yr)
        val = r.final_value
        val_age = age + yr
        remaining = max(0, 100_000_000 - val)
        color = "bright_green" if val >= 100_000_000 else "green" if val >= 50_000_000 else "cyan" if val >= 10_000_000 else "white"
        sim_table.add_row(
            f"{yr}年後",
            f"[{color}]{val:,.0f}円[/{color}]",
            f"{val_age}歳",
            f"[green]達成済み[/green]" if val >= 100_000_000 else f"あと{remaining:,.0f}円",
        )

    console.print(sim_table)

    console.print()
    console.print(Panel(
        f"  [bold]今すぐできる3つのアクション:[/bold]\n\n"
        f"  1. [cyan]証券口座を開設してNISAを設定[/cyan] → eMAXIS Slim全世界株式の積立を今日スタート\n"
        f"  2. [cyan]固定費を月2万円削減[/cyan] → その分を全額投資に回す\n"
        f"  3. [cyan]副業で月5万円の収入を目指す[/cyan] → スキルを棚卸しして最初の案件を取る",
        title="[bold bright_yellow]今日から始める行動計画[/bold bright_yellow]",
        border_style="bright_yellow",
    ))


@wealth.command("optimize")
@click.option("--capital", "-c", default=1_000_000, type=float, help="初期資金 (円)")
@click.option("--monthly", "-m", default=50_000, type=float, help="毎月積立額 (円)")
@click.option("--years", "-y", default=25, type=int, help="運用年数")
@click.option("--target", "-t", default=100_000_000, type=float, help="目標資産額 (円)")
@click.option("--sims", default=10000, type=int, help="モンテカルロ試行回数", show_default=True)
def wealth_optimize(capital: float, monthly: float, years: int, target: float, sims: int):
    """全戦略をモンテカルロ最適化して最も成功確率が高い手法を特定する\n\n例: python main.py wealth optimize -c 2000000 -m 80000 -y 25"""
    console.print()
    console.print(Panel(
        f"[bold white]初期資金:[/bold white] [cyan]{capital:,.0f}円[/cyan]  "
        f"[bold white]月積立:[/bold white] [cyan]{monthly:,.0f}円[/cyan]  "
        f"[bold white]目標:[/bold white] [yellow]{target:,.0f}円[/yellow]  "
        f"[bold white]期間:[/bold white] [cyan]{years}年[/cyan]  "
        f"[bold white]試行回数:[/bold white] [dim]{sims:,}回[/dim]",
        title="[bold blue]モンテカルロ最適化 — 全戦略確率解析[/bold blue]",
        border_style="blue",
    ))

    engine = MonteCarloEngine(n_simulations=sims)
    ranked = []

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as prog:
        task_id = prog.add_task("[cyan]全戦略をシミュレーション中...", total=None)
        for i, s in enumerate(STRATEGIES):
            prog.update(task_id, description=f"[cyan]シミュレーション中: {s.name_jp} ({i+1}/{len(STRATEGIES)})")
            r = engine.simulate(s, capital, monthly, years, target)
            ranked.append((s, r))
        ranked.sort(key=lambda x: (x[1].success_rate, x[1].median_outcome), reverse=True)

    table = Table(title=f"全戦略 成功確率ランキング ({sims:,}回試行)", box=box.ROUNDED,
                  title_style="bold yellow", border_style="yellow")
    table.add_column("順位", justify="center", width=4)
    table.add_column("戦略", style="bold", width=22)
    table.add_column("成功確率", justify="right")
    table.add_column("中央値(最終)", justify="right")
    table.add_column("悲観(10%)", justify="right", style="dim")
    table.add_column("楽観(90%)", justify="right")
    table.add_column("中央達成年", justify="right")
    table.add_column("月80%達成必要額", justify="right", style="dim")

    for rank, (s, r) in enumerate(ranked, 1):
        sc = r.success_rate
        sc_color = "bright_green" if sc >= 0.7 else "green" if sc >= 0.4 else "yellow" if sc >= 0.2 else "red"
        medal = {1: "◎", 2: "○", 3: "△"}.get(rank, " ")
        yr_label = f"{r.expected_years_median:.1f}年" if r.success_rate > 0.05 else "60年超"
        table.add_row(
            f"[{sc_color}]{medal}{rank}[/{sc_color}]",
            s.name_jp,
            f"[{sc_color}]{sc*100:.1f}%[/{sc_color}]",
            f"{r.median_outcome/1_000_000:.1f}百万円",
            f"{r.p10_outcome/1_000_000:.1f}百万円",
            f"[green]{r.p90_outcome/1_000_000:.1f}百万円[/green]",
            yr_label,
            f"{r.required_monthly_for_80pct:,.0f}円",
        )

    console.print()
    console.print(table)

    best_s, best_r = ranked[0]
    console.print()
    console.print(Panel(
        f"[bold]最適戦略:[/bold] [bright_green]{best_s.name_jp}[/bright_green]\n"
        f"[bold]成功確率:[/bold] [bright_green]{best_r.success_rate*100:.1f}%[/bright_green]  "
        f"[bold]中央値最終資産:[/bold] [cyan]{best_r.median_outcome:,.0f}円[/cyan]\n"
        f"[bold]楽観シナリオ(90%):[/bold] [green]{best_r.p90_outcome:,.0f}円[/green]  "
        f"[bold]悲観シナリオ(10%):[/bold] [red]{best_r.p10_outcome:,.0f}円[/red]\n\n"
        f"[dim]{best_s.description}[/dim]\n\n"
        f"[bold cyan]今すぐ実行すべきアクション:[/bold cyan]\n" +
        "\n".join(f"  {i+1}. {a}" for i, a in enumerate(best_s.action_steps)),
        title="[bold bright_green]最優秀戦略の詳細[/bold bright_green]",
        border_style="bright_green",
    ))

    # Efficient frontier using real data
    console.print()
    console.print(Rule("[bold yellow]効率的フロンティア — 数学的最適ポートフォリオ[/bold yellow]"))

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as prog:
        prog.add_task("[cyan]実市場データで最適ポートフォリオを計算中...", total=None)
        opt = EfficientFrontierOptimizer(period="3y")
        ok = opt.fetch_and_prepare()
        if ok:
            max_sharpe = opt.maximize_sharpe()
        else:
            max_sharpe = None

    if max_sharpe:
        opt_table = Table(title="シャープ比最大化ポートフォリオ (実データ 3年)", box=box.ROUNDED,
                          title_style="bold cyan", border_style="cyan")
        opt_table.add_column("ティッカー", style="bold")
        opt_table.add_column("銘柄名", style="dim")
        opt_table.add_column("最適比率", justify="right")
        opt_table.add_column("投資額", justify="right")

        for tkr, nm, w in sorted(
            zip(max_sharpe.tickers, max_sharpe.names, max_sharpe.weights),
            key=lambda x: x[2], reverse=True
        ):
            if w >= 0.02:
                opt_table.add_row(
                    tkr, nm,
                    f"[{'bright_green' if w >= 0.15 else 'green'}]{w*100:.1f}%[/]",
                    f"{capital * w:,.0f}円",
                )

        console.print(opt_table)
        console.print(
            f"\n  [bold]期待年率:[/bold] [cyan]{max_sharpe.expected_annual_return*100:.1f}%[/cyan]  "
            f"[bold]期待ボラ:[/bold] [yellow]{max_sharpe.expected_volatility*100:.1f}%[/yellow]  "
            f"[bold]シャープ比:[/bold] [green]{max_sharpe.sharpe_ratio:.2f}[/green]"
        )


@wealth.command("screen")
@click.option("--top", "-n", default=10, type=int, help="上位N銘柄を表示", show_default=True)
def wealth_screen(top: int):
    """実データで投資候補銘柄をスクリーニングする\n\n例: python main.py wealth screen --top 10"""
    console.print()
    console.print(Panel(
        "割安度・成長性・収益性・モメンタムを実データで多角評価",
        title="[bold blue]リアルタイム銘柄スクリーニング[/bold blue]",
        border_style="blue",
    ))

    screener = StockScreener(top_n=top)
    results = []

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as prog:
        task_id = prog.add_task("[cyan]銘柄データ取得中...", total=None)

        def cb(ticker, i, total):
            prog.update(task_id, description=f"[cyan]スクリーニング中: {ticker} ({i}/{total})")

        results = screener.run(progress_callback=cb)

    if not results:
        console.print("[red]データ取得に失敗しました。ネット接続を確認してください。[/red]")
        return

    table = Table(title=f"投資候補ランキング TOP{top}", box=box.ROUNDED,
                  title_style="bold yellow", border_style="yellow")
    table.add_column("順位", justify="center", width=4)
    table.add_column("銘柄", style="bold")
    table.add_column("名称", style="dim", width=20)
    table.add_column("スコア", justify="center")
    table.add_column("現在値", justify="right")
    table.add_column("PER", justify="right")
    table.add_column("PBR", justify="right")
    table.add_column("ROE", justify="right")
    table.add_column("配当%", justify="right")
    table.add_column("1Y騰落", justify="right")
    table.add_column("テクニカル", justify="center")

    for rank, s in enumerate(results, 1):
        sc_color = "bright_green" if s.score >= 75 else "green" if s.score >= 60 else "yellow" if s.score >= 45 else "red"
        mom_color = "green" if (s.momentum_1y or 0) >= 0 else "red"
        tech_color = {"強い上昇": "bright_green", "上昇": "green", "中立": "yellow",
                      "下降": "red", "強い下降": "bright_red"}.get(s.technical_signal, "white")
        table.add_row(
            f"{rank}",
            s.ticker,
            s.name[:18],
            f"[{sc_color}]{s.score}[/{sc_color}]",
            f"{s.current_price:,.2f}{s.currency}",
            f"{s.pe_ratio}" if s.pe_ratio else "[dim]N/A[/dim]",
            f"{s.pb_ratio}" if s.pb_ratio else "[dim]N/A[/dim]",
            f"{s.roe}%" if s.roe else "[dim]N/A[/dim]",
            f"{s.dividend_yield}%" if s.dividend_yield else "[dim]-[/dim]",
            f"[{mom_color}]{'+' if (s.momentum_1y or 0) >= 0 else ''}{s.momentum_1y}%[/{mom_color}]" if s.momentum_1y is not None else "[dim]N/A[/dim]",
            f"[{tech_color}]{s.technical_signal}[/{tech_color}]",
        )

    console.print(table)

    if results:
        top3 = results[:3]
        console.print()
        for s in top3:
            if s.buy_reasons or s.risk_flags:
                reasons_text = "\n".join(f"  [green]✓[/green] {r}" for r in s.buy_reasons)
                flags_text = "\n".join(f"  [red]⚠[/red] {f}" for f in s.risk_flags)
                console.print(Panel(
                    (reasons_text + ("\n" + flags_text if flags_text else "")),
                    title=f"[bold]{s.ticker} {s.name} (スコア:{s.score})[/bold]",
                    border_style="green" if not s.risk_flags else "yellow",
                ))


@wealth.command("execute")
@click.option("--capital", "-c", default=1_000_000, type=float, help="現在の総資産 (円)")
@click.option("--monthly", "-m", default=50_000, type=float, help="毎月の投資予算 (円)")
@click.option("--age", "-a", default=30, type=int, help="年齢")
@click.option("--months", default=12, type=int, help="実行計画の月数", show_default=True)
@click.option("--nisa/--no-nisa", default=False, help="NISA口座開設済み")
@click.option("--ideco/--no-ideco", default=False, help="iDeCo口座開設済み")
@click.option("--self-employed/--employee", default=False, help="自営業かどうか")
@click.option("--with-screen/--no-screen", default=False, help="銘柄スクリーニングを実行して組み込む")
def wealth_execute(capital: float, monthly: float, age: int, months: int,
                   nisa: bool, ideco: bool, self_employed: bool, with_screen: bool):
    """億万長者への具体的実行カレンダーを生成する\n\n例: python main.py wealth execute -c 2000000 -m 100000 --age 30 --with-screen"""
    console.print()
    console.print(Panel(
        f"[bold white]資産:[/bold white] [cyan]{capital:,.0f}円[/cyan]  "
        f"[bold white]月投資額:[/bold white] [cyan]{monthly:,.0f}円[/cyan]  "
        f"[bold white]年齢:[/bold white] [cyan]{age}歳[/cyan]  "
        f"[bold white]期間:[/bold white] [cyan]{months}ヶ月[/cyan]  "
        f"{'[green]NISA済[/green]' if nisa else '[red]NISA未[/red]'}  "
        f"{'[green]iDeCo済[/green]' if ideco else '[red]iDeCo未[/red]'}",
        title="[bold blue]億万長者 実行カレンダー生成[/bold blue]",
        border_style="blue",
    ))

    top_stocks = []
    optimal_tickers = []

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as prog:
        if with_screen:
            prog.add_task("[cyan]銘柄スクリーニング実行中...", total=None)
            try:
                top_stocks = StockScreener(top_n=5).run()
            except Exception:
                pass

        prog.add_task("[cyan]最適ポートフォリオ計算中...", total=None)
        opt = EfficientFrontierOptimizer(period="2y")
        if opt.fetch_and_prepare():
            pf = opt.maximize_sharpe()
            optimal_tickers = [t for t, w in zip(pf.tickers, pf.weights) if w >= 0.08]

    planner = ExecutionPlanner(
        initial_capital=capital,
        monthly_budget=monthly,
        age=age,
        is_self_employed=self_employed,
        has_nisa=nisa,
        has_ideco=ideco,
        optimal_tickers=optimal_tickers,
        top_stocks=top_stocks,
    )
    plan = planner.generate(months=months)

    # Summary
    console.print()
    console.print(Panel(plan.summary, title="[bold]月次投資配分サマリー[/bold]", border_style="cyan"))

    # Month-by-month calendar
    priority_color = {"HIGH": "bright_red", "MEDIUM": "yellow", "LOW": "dim"}
    category_icon = {"SETUP": "⚙", "INVEST": "💰", "TAX": "🧾", "REVIEW": "📊"}
    category_color = {"SETUP": "cyan", "INVEST": "green", "TAX": "magenta", "REVIEW": "blue"}

    console.print()
    console.print(Rule("[bold yellow]実行カレンダー[/bold yellow]"))

    by_month = plan.by_month(months)
    for m in range(months):
        tasks = by_month.get(m, [])
        if not tasks:
            continue

        month_label = tasks[0].date_label
        total_invest = sum(t.amount_jpy for t in tasks if t.category == "INVEST")

        task_lines = []
        for t in sorted(tasks, key=lambda x: (0 if x.priority == "HIGH" else 1 if x.priority == "MEDIUM" else 2)):
            pc = priority_color.get(t.priority, "white")
            cc = category_color.get(t.category, "white")
            icon = category_icon.get(t.category, "•")
            amount_str = f" [cyan]{t.amount_jpy:,.0f}円[/cyan]" if t.amount_jpy > 0 else ""
            note_str = f"\n       [dim]{t.note}[/dim]" if t.note else ""
            task_lines.append(
                f"  [{pc}][{t.priority}][/{pc}] [{cc}]{icon} {t.action}[/{cc}]{amount_str}{note_str}"
            )

        invest_str = f"  投資合計: [bold cyan]{total_invest:,.0f}円[/bold cyan]" if total_invest > 0 else ""
        console.print(Panel(
            "\n".join(task_lines) + ("\n\n" + invest_str if invest_str else ""),
            title=f"[bold]{month_label}[/bold]",
            border_style="blue" if m > 0 else "bright_blue",
        ))

    # 1-year summary stats
    total_invested = monthly * months
    sim = CompoundGrowthSimulator(capital, 0.07, monthly)
    result = sim.simulate(years=months // 12 + 1, target=100_000_000)
    console.print()
    console.print(Panel(
        f"  [bold]この{months}ヶ月の総投資予定額:[/bold] [cyan]{total_invested:,.0f}円[/cyan]\n"
        f"  [bold]年率7%想定での{months}ヶ月後資産:[/bold] [cyan]{result.year_by_year[min(months//12+1, len(result.year_by_year)-1)][1]:,.0f}円[/cyan]\n"
        f"  [bold]1億円達成予測:[/bold] "
        + (f"[bright_green]約{result.years_to_target}年後[/bright_green]" if result.years_to_target else "[yellow]60年超（月積立増加を検討）[/yellow]"),
        title="[bold]実行計画サマリー[/bold]",
        border_style="bright_yellow",
    ))


if __name__ == "__main__":
    cli()
