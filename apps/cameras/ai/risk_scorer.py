"""
IBVAP Real-Time Risk Scoring Engine
Calculates transparent application-level risk scores (0–100) and severity tiers
based on configurable weights from SystemConfiguration and detected context factors.
"""

from apps.settings_app.models import SystemConfiguration


class RiskScorer:
    @staticmethod
    def calculate_risk(event_type, object_type, is_night=False, is_restricted=False, is_loitering=False, is_multi=False, watchlist_match=False):
        """
        Calculates threat score and severity level based on active SystemConfiguration weights.
        Returns:
            dict: {
                'threat_score': int (0-100),
                'severity': 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL',
                'reason': str,
                'breakdown': list of dicts
            }
        """
        try:
            config = SystemConfiguration.get_settings()
        except Exception:
            config = None

        w_person = getattr(config, 'weight_person_detection', 20) if config else 20
        w_night = getattr(config, 'weight_night_movement', 15) if config else 15
        w_zone = getattr(config, 'weight_restricted_zone', 30) if config else 30
        w_loitering = getattr(config, 'weight_loitering', 10) if config else 10
        w_watchlist = getattr(config, 'weight_watchlist_vehicle', 40) if config else 40

        score = 0
        reasons = []
        breakdown = []

        if object_type == 'Person' or event_type in {'INTRUSION', 'VIRTUAL_FENCE_INTRUSION', 'LOITERING', 'NIGHT_MOVEMENT'}:
            score += w_person
            reasons.append("Person detection")
            breakdown.append({'factor': 'Human Detection', 'points': f"+{w_person}"})

        if event_type == 'VIRTUAL_FENCE_INTRUSION' or is_restricted:
            score += w_zone
            reasons.append("Restricted zone breach")
            breakdown.append({'factor': 'Virtual Fence Breach', 'points': f"+{w_zone}"})

        if is_night or event_type == 'NIGHT_MOVEMENT':
            score += w_night
            reasons.append("Low-light night conditions")
            breakdown.append({'factor': 'Night Condition', 'points': f"+{w_night}"})

        if is_loitering or event_type == 'LOITERING':
            score += w_loitering
            reasons.append("Extended loitering")
            breakdown.append({'factor': 'Perimeter Loitering', 'points': f"+{w_loitering}"})

        if is_multi or event_type == 'MULTIPLE_PERSON_INTRUSION':
            score += 20
            reasons.append("Multiple subjects")
            breakdown.append({'factor': 'Multi-Person Breach', 'points': "+20"})

        if watchlist_match or event_type == 'ANPR_MATCH':
            score += w_watchlist
            reasons.append("Watchlist intercept match")
            breakdown.append({'factor': 'Watchlist Match', 'points': f"+{w_watchlist}"})

        # Cap between 0 and 100
        score = max(5, min(100, score))

        if score >= 70:
            severity = 'CRITICAL'
        elif score >= 50:
            severity = 'HIGH'
        elif score >= 30:
            severity = 'MEDIUM'
        else:
            severity = 'LOW'

        reason_str = " | ".join(reasons) if reasons else "Routine perimeter telemetry"

        return {
            'threat_score': score,
            'severity': severity,
            'reason': reason_str,
            'breakdown': breakdown
        }
