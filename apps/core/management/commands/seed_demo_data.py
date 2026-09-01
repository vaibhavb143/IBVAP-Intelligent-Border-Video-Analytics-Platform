from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from apps.accounts.models import UserProfile
from apps.cameras.models import Camera
from apps.alerts.models import SecurityAlert
from apps.events.models import SecurityEvent
from apps.anpr.models import ANPRDetection
from apps.watchlist.models import WatchlistVehicle
from apps.settings_app.models import SystemConfiguration

class Command(BaseCommand):
    help = 'Seeds database with realistic SIH Command Center demo data for IBVAP'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Initializing IBVAP Command Center Database Seeding...'))

        # 1. Create Default Administrative & Officer Users
        admin_user, created_admin = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@ibvap.gov.in',
                'first_name': 'Commanding',
                'last_name': 'Officer',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created_admin:
            admin_user.set_password('ibvap@2026')
            admin_user.save()
            admin_user.profile.role = 'ADMIN'
            admin_user.profile.badge_number = 'BSF-CMD-001'
            admin_user.profile.sector_assignment = 'HQ Tactical Operations Center'
            admin_user.profile.save()
            self.stdout.write(self.style.SUCCESS('Created Admin account: admin / ibvap@2026'))
        else:
            self.stdout.write(self.style.SUCCESS('Admin account already exists.'))

        officer_user, created_officer = User.objects.get_or_create(
            username='officer_singh',
            defaults={
                'email': 'singh.raj@ibvap.gov.in',
                'first_name': 'Rajveer',
                'last_name': 'Singh',
                'is_staff': False,
            }
        )
        if created_officer:
            officer_user.set_password('ibvap@2026')
            officer_user.save()
            officer_user.profile.role = 'OFFICER'
            officer_user.profile.badge_number = 'BSF-SEC-042'
            officer_user.profile.sector_assignment = 'Forward Sector 01-B'
            officer_user.profile.save()
            self.stdout.write(self.style.SUCCESS('Created Officer account: officer_singh / ibvap@2026'))

        # 2. Seed Cameras
        cameras_data = [
            {
                'camera_id': 'BOP-01',
                'name': 'Forward Outpost Alpha (Webcam Live Feed)',
                'location': 'Sector 01 — Northern Ridge',
                'feed_type': 'LIVE',
                'source_type': 'WEBCAM',
                'source_url': '0',
                'status': 'ONLINE',
                'people_count': 4,
                'vehicle_count': 1,
                'threat_level': 'HIGH',
                'enable_human_detection': True,
                'enable_vehicle_detection': True,
                'enable_anpr': False,
                'enable_intrusion_detection': True,
                'enable_night_detection': True,
                'latitude': 32.7310,
                'longitude': 74.8520,
            },
            {
                'camera_id': 'BOP-02',
                'name': 'Perimeter Outpost Bravo (Video Stream)',
                'location': 'Sector 02 — Eastern Lowlands',
                'feed_type': 'SIMULATION',
                'source_type': 'VIDEO_FILE',
                'source_url': 'sim_bop_02.mp4',
                'status': 'ONLINE',
                'people_count': 2,
                'vehicle_count': 0,
                'threat_level': 'NORMAL',
                'enable_human_detection': True,
                'enable_vehicle_detection': True,
                'enable_anpr': False,
                'enable_intrusion_detection': True,
                'enable_night_detection': True,
                'latitude': 32.7240,
                'longitude': 74.8610,
            },
            {
                'camera_id': 'BOP-03',
                'name': 'Zero Line Virtual Fence (Video Stream)',
                'location': 'Sector 03 — Restricted Outpost',
                'feed_type': 'SIMULATION',
                'source_type': 'VIDEO_FILE',
                'source_url': 'sim_bop_03.mp4',
                'status': 'ONLINE',
                'people_count': 1,
                'vehicle_count': 0,
                'threat_level': 'CRITICAL',
                'enable_human_detection': True,
                'enable_vehicle_detection': False,
                'enable_anpr': False,
                'enable_intrusion_detection': True,
                'enable_night_detection': True,
                'latitude': 32.7380,
                'longitude': 74.8480,
            },
            {
                'camera_id': 'GATE-01',
                'name': 'Main Checkpost & Access Barrier',
                'location': 'Sector 01 — Main Checkpost Entry',
                'feed_type': 'SIMULATION',
                'source_type': 'VIDEO_FILE',
                'source_url': 'sim_gate_01.mp4',
                'status': 'ONLINE',
                'people_count': 8,
                'vehicle_count': 6,
                'threat_level': 'HIGH',
                'enable_human_detection': True,
                'enable_vehicle_detection': True,
                'enable_anpr': True,
                'enable_intrusion_detection': True,
                'enable_night_detection': False,
                'latitude': 32.7210,
                'longitude': 74.8450,
            },
        ]

        created_cameras = {}
        for cam in cameras_data:
            obj, _ = Camera.objects.update_or_create(
                camera_id=cam['camera_id'],
                defaults=cam
            )
            created_cameras[cam['camera_id']] = obj

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_cameras)} tactical cameras."))

        # 3. Seed Watchlist Vehicles
        watchlist_data = [
            {
                'plate_number': 'MH20AB1234',
                'vehicle_type': 'Car',
                'description': 'Flagged for suspicious loitering near BOP Sector 1 border corridor (Demo Watchlist Item)',
                'risk_level': 'HIGH',
                'status': 'Active',
                'reported_sector': 'GATE-01 Main Gate Entry',
            },
            {
                'plate_number': 'DL01XY9988',
                'vehicle_type': 'Truck',
                'description': 'Commercial carrier flagged for unauthorized off-hours border approach (Demo Watchlist Item)',
                'risk_level': 'HIGH',
                'status': 'Active',
                'reported_sector': 'Sector 02 Freight Route',
            },
            {
                'plate_number': 'KA05MN8899',
                'vehicle_type': 'SUV',
                'description': 'High-risk intercept target identified in intelligence bulletin #2026-BOP',
                'risk_level': 'CRITICAL',
                'status': 'Active',
                'reported_sector': 'Sector 03 Buffer Zone',
            },
            {
                'plate_number': 'HR26DQ1024',
                'vehicle_type': 'Car',
                'description': 'Vehicle previously cleared following mandatory security scan',
                'risk_level': 'LOW',
                'status': 'Resolved',
                'reported_sector': 'Main Checkpost',
            }
        ]

        for w in watchlist_data:
            WatchlistVehicle.objects.update_or_create(
                plate_number=w['plate_number'],
                defaults=w
            )

        self.stdout.write(self.style.SUCCESS("Seeded Watchlist vehicle database."))

        # 4. Seed Security Alerts
        now = timezone.now()
        alerts_data = [
            {
                'alert_id': 'ALT-2026-901',
                'title': 'Restricted Zone Intrusion',
                'camera': created_cameras['BOP-03'],
                'severity': 'CRITICAL',
                'threat_score': 92,
                'status': 'ACTIVE',
                'detected_object': 'Person (Unidentified)',
                'description': 'AI Virtual Fence breach detected. Individual crossed designated 50-meter buffer zone at 02:17:32 IST.',
            },
            {
                'alert_id': 'ALT-2026-902',
                'title': 'Watchlist Vehicle Detected',
                'camera': created_cameras['GATE-01'],
                'severity': 'HIGH',
                'threat_score': 80,
                'status': 'ACTIVE',
                'detected_object': 'Vehicle (MH20AB1234)',
                'description': 'ANPR OCR matched license plate MH20AB1234 against High Risk watchlist at Main Checkpost.',
            },
            {
                'alert_id': 'ALT-2026-903',
                'title': 'Night Movement Detected',
                'camera': created_cameras['BOP-01'],
                'severity': 'MEDIUM',
                'threat_score': 70,
                'status': 'ACTIVE',
                'detected_object': 'Person (Low-light thermal/contrast motion)',
                'description': 'Significant thermal movement cluster identified during active night surveillance curfew (03:04:19 IST).',
            },
            {
                'alert_id': 'ALT-2026-904',
                'title': 'Perimeter Loitering Warning',
                'camera': created_cameras['BOP-02'],
                'severity': 'LOW',
                'threat_score': 35,
                'status': 'RESOLVED',
                'detected_object': 'Person',
                'description': 'Stationary object tracked near fence line for >180 seconds. Cleared as local patrol sweep.',
            },
        ]

        for a in alerts_data:
            SecurityAlert.objects.update_or_create(
                alert_id=a['alert_id'],
                defaults=a
            )

        self.stdout.write(self.style.SUCCESS("Seeded Live Security Alerts."))

        # 5. Seed Historical Events
        events_data = [
            {
                'event_id': 'EVT-021732',
                'camera': created_cameras['BOP-03'],
                'event_type': 'INTRUSION',
                'object_type': 'Person',
                'threat_score': 92,
                'severity': 'CRITICAL',
                'confidence': 0.96,
                'coordinates': '32.7380 N, 74.8480 E',
                'details': 'AI Virtual Fence breach detected. Unidentified individual crossed designated 50-meter buffer zone.',
                'timestamp': now - timedelta(minutes=14),
            },
            {
                'event_id': 'EVT-022104',
                'camera': created_cameras['GATE-01'],
                'event_type': 'ANPR_MATCH',
                'object_type': 'Vehicle',
                'threat_score': 80,
                'severity': 'HIGH',
                'confidence': 0.98,
                'coordinates': '32.7210 N, 74.8450 E',
                'details': 'Automated plate recognition matched MH20AB1234 with High Risk contraband watchlist.',
                'timestamp': now - timedelta(minutes=10),
            },
            {
                'event_id': 'EVT-030419',
                'camera': created_cameras['BOP-01'],
                'event_type': 'NIGHT_MOVEMENT',
                'object_type': 'Person',
                'threat_score': 70,
                'severity': 'HIGH',
                'confidence': 0.91,
                'coordinates': '32.7310 N, 74.8520 E',
                'details': 'Low-light motion trajectory detected near barbed wire sector during restricted hours.',
                'timestamp': now - timedelta(minutes=5),
            },
            {
                'event_id': 'EVT-031542',
                'camera': created_cameras['BOP-02'],
                'event_type': 'LOITERING',
                'object_type': 'Person',
                'threat_score': 45,
                'severity': 'MEDIUM',
                'confidence': 0.93,
                'coordinates': '32.7240 N, 74.8610 E',
                'details': 'Subject dwelling in surveillance Sector 02 buffer perimeter for over 3 minutes.',
                'timestamp': now - timedelta(minutes=25),
            },
            {
                'event_id': 'EVT-033100',
                'camera': created_cameras['GATE-01'],
                'event_type': 'UNAUTHORIZED_VEHICLE',
                'object_type': 'Vehicle',
                'threat_score': 65,
                'severity': 'HIGH',
                'confidence': 0.95,
                'coordinates': '32.7210 N, 74.8450 E',
                'details': 'Vehicle entered checkpoint approach corridor without RF-ID broadcast signal.',
                'timestamp': now - timedelta(minutes=45),
            },
            {
                'event_id': 'EVT-035210',
                'camera': created_cameras['BOP-01'],
                'event_type': 'PERIMETER_CROSSING',
                'object_type': 'Animal',
                'threat_score': 20,
                'severity': 'LOW',
                'confidence': 0.89,
                'coordinates': '32.7310 N, 74.8520 E',
                'details': 'Wildlife motion classification filtered by AI model. Non-threat event.',
                'timestamp': now - timedelta(hours=1, minutes=10),
            },
        ]

        for e in events_data:
            SecurityEvent.objects.update_or_create(
                event_id=e['event_id'],
                defaults=e
            )

        self.stdout.write(self.style.SUCCESS("Seeded Historical Security Events."))

        # 6. Seed ANPR Records
        anpr_data = [
            {
                'camera': created_cameras['GATE-01'],
                'plate_number': 'MH20AB1234',
                'vehicle_type': 'Car',
                'confidence': 0.96,
                'is_watchlist_match': True,
                'match_status': 'MATCH',
                'watchlist_risk': 'HIGH',
                'speed_estimate': '38 km/h',
                'direction': 'Inbound Approach',
            },
            {
                'camera': created_cameras['GATE-01'],
                'plate_number': 'DL01XY9988',
                'vehicle_type': 'Truck',
                'confidence': 0.94,
                'is_watchlist_match': True,
                'match_status': 'MATCH',
                'watchlist_risk': 'HIGH',
                'speed_estimate': '25 km/h',
                'direction': 'Inbound Heavy Lane',
            },
            {
                'camera': created_cameras['GATE-01'],
                'plate_number': 'JK02AZ7711',
                'vehicle_type': 'SUV',
                'confidence': 0.98,
                'is_watchlist_match': False,
                'match_status': 'CLEARED',
                'watchlist_risk': 'NORMAL',
                'speed_estimate': '44 km/h',
                'direction': 'Outbound',
            },
            {
                'camera': created_cameras['GATE-01'],
                'plate_number': 'PB08CB4432',
                'vehicle_type': 'Motorcycle',
                'confidence': 0.92,
                'is_watchlist_match': False,
                'match_status': 'CLEARED',
                'watchlist_risk': 'NORMAL',
                'speed_estimate': '32 km/h',
                'direction': 'Inbound Checkpoint',
            },
            {
                'camera': created_cameras['GATE-01'],
                'plate_number': 'HR26DQ1024',
                'vehicle_type': 'Car',
                'confidence': 0.97,
                'is_watchlist_match': False,
                'match_status': 'CLEARED',
                'watchlist_risk': 'NORMAL',
                'speed_estimate': '40 km/h',
                'direction': 'Inbound',
            },
        ]

        for p in anpr_data:
            ANPRDetection.objects.create(**p)

        self.stdout.write(self.style.SUCCESS("Seeded ANPR Recognition Records."))

        # 7. Initialize Default System Settings
        SystemConfiguration.get_settings()
        self.stdout.write(self.style.SUCCESS("Initialized System Configuration."))

        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] IBVAP Phase 1 Command Center Database Seeding Complete!"))
