"""
services/report_service.py
===========================
Generates PDF and CSV reports. Saves them to /reports folder.
Uses ReportLab for PDF — completely free, no external services.
"""

import csv
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer
)

from config.settings import settings
from database.repositories.report_repository import ReportRepository
from services.analytics_service import AnalyticsService
from services.campaign_service import CampaignService

logger = logging.getLogger(__name__)


class ReportService:

    def __init__(self):
        self.report_repo     = ReportRepository()
        self.analytics_svc   = AnalyticsService()
        self.campaign_svc    = CampaignService()
        self.reports_dir     = settings.REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _filename(self, prefix: str, fmt: str) -> str:
        """Generate a unique filename with timestamp."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{ts}.{fmt}"

    def generate_weekly_pdf(self, user_id: Optional[int] = None) -> str:
        """
        Generate a weekly performance PDF report.

        Returns:
            File path of the generated PDF.
        """
        filename  = self._filename("weekly_report", "pdf")
        file_path = str(self.reports_dir / filename)

        kpis      = self.analytics_svc.get_dashboard_kpis(7)
        top_camps = self.analytics_svc.get_top_campaigns(7)
        worst     = self.analytics_svc.get_worst_campaigns(7)
        comparison = self.analytics_svc.get_platform_comparison(7)

        doc    = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story  = []

        # ── Title ─────────────────────────────────────────────────────────────
        title_style = ParagraphStyle(
            "Title", parent=styles["Title"],
            fontSize=24, textColor=colors.HexColor("#6366f1"),
            spaceAfter=6
        )
        story.append(Paragraph("AdPulse Weekly Report", title_style))
        story.append(Paragraph(
            f"Period: Last 7 days  |  Generated: {datetime.now().strftime('%d %b %Y %H:%M')}",
            styles["Normal"]
        ))
        story.append(Spacer(1, 0.3 * inch))

        # ── KPI Summary Table ─────────────────────────────────────────────────
        story.append(Paragraph("Performance Summary", styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))

        kpi_data = [
            ["Metric", "Value"],
            ["Total Spend",       f"Rs {kpis.get('total_spend', 0):,.2f}"],
            ["Total Revenue",     f"Rs {kpis.get('total_revenue', 0):,.2f}"],
            ["Average ROI",       f"{kpis.get('avg_roi', 0):.2f}x"],
            ["Total Clicks",      f"{kpis.get('total_clicks', 0):,}"],
            ["Total Conversions", f"{kpis.get('total_conversions', 0):,}"],
            ["Average CTR",       f"{kpis.get('avg_ctr', 0):.2f}%"],
        ]

        kpi_table = Table(kpi_data, colWidths=[3 * inch, 3 * inch])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#6366f1")),
            ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 11),
            ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8f9fa"), colors.white]),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING",  (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 0.3 * inch))

        # ── Platform Breakdown ────────────────────────────────────────────────
        if comparison:
            story.append(Paragraph("Platform Breakdown", styles["Heading2"]))
            story.append(Spacer(1, 0.1 * inch))

            plat_data = [["Platform", "Spend", "Revenue", "ROI", "CTR"]]
            for row in comparison:
                plat_data.append([
                    row.get("platform", "").title(),
                    f"Rs {row.get('total_spend', 0):,.2f}",
                    f"Rs {row.get('total_revenue', 0):,.2f}",
                    f"{row.get('avg_roi', 0):.2f}x",
                    f"{row.get('avg_ctr', 0):.2f}%",
                ])

            plat_table = Table(plat_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1*inch, 1*inch])
            plat_table.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#0ea5e9")),
                ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
                ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",    (0, 0), (-1, -1), 10),
                ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0f9ff"), colors.white]),
                ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING",  (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]))
            story.append(plat_table)
            story.append(Spacer(1, 0.3 * inch))

        # ── Top Campaigns ─────────────────────────────────────────────────────
        if top_camps:
            story.append(Paragraph("Top Performing Campaigns", styles["Heading2"]))
            story.append(Spacer(1, 0.1 * inch))

            top_data = [["Campaign", "Platform", "ROI", "Conversions", "Spend"]]
            for c in top_camps[:5]:
                top_data.append([
                    c.get("name", "")[:30],
                    c.get("platform", "").title(),
                    f"{c.get('avg_roi', 0):.2f}x",
                    str(c.get("total_conversions", 0)),
                    f"Rs {c.get('total_spend', 0):,.2f}",
                ])

            top_table = Table(top_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1.2*inch, 1.3*inch])
            top_table.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#10b981")),
                ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
                ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",    (0, 0), (-1, -1), 9),
                ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0fdf4"), colors.white]),
                ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING",  (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(top_table)

        # ── Footer ────────────────────────────────────────────────────────────
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(
            "Generated by AdPulse AI Marketing Intelligence Platform",
            styles["Normal"]
        ))

        doc.build(story)
        logger.info("Weekly PDF report generated: %s", file_path)

        self.report_repo.create(
            title=f"Weekly Report — {datetime.now().strftime('%d %b %Y')}",
            report_type="weekly",
            fmt="pdf",
            file_path=file_path,
            generated_by=user_id
        )
        return file_path

    def export_campaigns_csv(self, user_id: Optional[int] = None) -> str:
        """
        Export all campaigns to a CSV file.

        Returns:
            File path of the generated CSV.
        """
        filename  = self._filename("campaigns_export", "csv")
        file_path = str(self.reports_dir / filename)

        campaigns = self.campaign_svc.get_all()

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "id", "name", "platform", "status", "objective",
                "daily_budget", "total_budget", "spent_total",
                "health_score", "start_date", "created_at"
            ])
            writer.writeheader()
            for camp in campaigns:
                writer.writerow({k: camp.get(k, "") for k in writer.fieldnames})

        logger.info("CSV export generated: %s", file_path)

        self.report_repo.create(
            title=f"Campaigns Export — {datetime.now().strftime('%d %b %Y')}",
            report_type="campaign",
            fmt="csv",
            file_path=file_path,
            generated_by=user_id
        )
        return file_path