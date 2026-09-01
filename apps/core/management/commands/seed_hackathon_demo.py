from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.watchlist.models import WatchlistPerson, WatchlistVehicle
from apps.cameras.models import Camera
from apps.events.models import SecurityEvent
from apps.alerts.models import SecurityAlert


class Command(BaseCommand):
    help = "Seed initial demonstration data for Hackathon evaluation (FRS, Behavioral, ANPR)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Hackathon Demo Intelligence Data..."))

        # 1. Seed Watchlist Persons (Biometric FRS)
        persons_data = [
            {
                'person_id': 'FRS-IND-042',
                'full_name': 'Tariq Mahmood',
                'alias': 'Tiger / Falcon-9',
                'category': 'INFILTRATOR',
                'threat_level': 'CRITICAL',
                'status': 'Active',
                'facial_embedding_id': 'EMB_77AF92_VECTOR_128',
                'last_seen_sector': 'Sector 01 - Forward Post Alpha (Zero Line)',
                'reason_for_flagging': 'Primary suspect in cross-border covert reconnaissance. Armed and high flight risk.',
            },
            {
                'person_id': 'FRS-IND-088',
                'full_name': 'Rashid Khan',
                'alias': 'Subedar / RK',
                'category': 'SMUGGLER',
                'threat_level': 'HIGH',
                'status': 'Active',
                'facial_embedding_id': 'EMB_88CC14_VECTOR_128',
                'last_seen_sector': 'Sector 02 - Riverine Crossing Point',
                'reason_for_flagging': 'Contraband courier operative active along western riverine gaps.',
            },
            {
                'person_id': 'FRS-IND-105',
                'full_name': 'Vikas Rathore',
                'alias': 'Shadow-3',
                'category': 'SUSPECT',
                'threat_level': 'MEDIUM',
                'status': 'Investigating',
                'facial_embedding_id': 'EMB_1105BB_VECTOR_128',
                'last_seen_sector': 'Sector 03 - Highway Checkpoint Gate 02',
                'reason_for_flagging': 'Unauthorized drone transmitter operator detected in buffer zone.',
            },
            {
                'person_id': 'FRS-IND-119',
                'full_name': 'Haroon Al-Masri',
                'alias': 'Engineer',
                'category': 'INFILTRATOR',
                'threat_level': 'CRITICAL',
                'status': 'Active',
                'facial_embedding_id': 'EMB_9921AA_VECTOR_128',
                'last_seen_sector': 'Sector 04 - Southern Ridge Perimeter',
                'reason_for_flagging': 'Perimeter sensor tampering specialist. Intercept on sight order issued.',
            },
        ]

        for p_data in persons_data:
            obj, created = WatchlistPerson.objects.get_or_create(
                person_id=p_data['person_id'],
                defaults=p_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  + Created FRS Person: {obj.full_name} ({obj.person_id})"))

        # 2. Ensure cameras have FRS and behavioral analytics active
        Camera.objects.all().update(
            enable_frs=True,
            enable_behavioral_analytics=True,
            is_ai_active=True
        )

        camera_alpha = Camera.objects.filter(camera_id='BOP-01').first() or Camera.objects.first()
        camera_beta = Camera.objects.filter(camera_id='BOP-02').first() or camera_alpha

        # 3. Seed Behavioral & FRS Security Events
        now = timezone.now()
        events_data = [
            {
                'event_id': 'EVT-FRS-901',
                'camera': camera_alpha,
                'event_type': 'FRS_MATCH',
                'object_type': 'Person',
                'threat_score': 95,
                'severity': 'CRITICAL',
                'details': 'Biometric Facial Match confirmed: Tariq Mahmood (FRS-IND-042). Optical confidence: 96.4%.',
                'confidence': 0.96,
                'coordinates': '32.7266 N, 74.8570 E',
                'timestamp': now - timedelta(minutes=14),
            },
            {
                'event_id': 'EVT-BEH-902',
                'camera': camera_alpha,
                'event_type': 'CRAWLING_CONCEALMENT',
                'object_type': 'Person',
                'threat_score': 88,
                'severity': 'CRITICAL',
                'details': 'Low-crawl / prone stealth movement detected across 50m restricted vegetation corridor.',
                'confidence': 0.93,
                'coordinates': '32.7271 N, 74.8582 E',
                'timestamp': now - timedelta(minutes=45),
            },
            {
                'event_id': 'EVT-BEH-903',
                'camera': camera_beta,
                'event_type': 'SUSPICIOUS_PACKAGE_DROP',
                'object_type': 'Package',
                'threat_score': 82,
                'severity': 'HIGH',
                'details': 'Static object abandoned near fence line by unidentified runner. Blast/Contraband quarantine flagged.',
                'confidence': 0.91,
                'coordinates': '32.7210 N, 74.8620 E',
                'timestamp': now - timedelta(hours=2, minutes=10),
            },
            {
                'event_id': 'EVT-BEH-904',
                'camera': camera_alpha,
                'event_type': 'LOITERING',
                'object_type': 'Person',
                'threat_score': 74,
                'severity': 'MEDIUM',
                'details': 'Individual observed pacing along sector perimeter fence boundary for > 180 seconds.',
                'confidence': 0.89,
                'coordinates': '32.7255 N, 74.8560 E',
                'timestamp': now - timedelta(hours=4, minutes=30),
            },
        ]

        for e_data in events_data:
            if camera_alpha:
                obj, created = SecurityEvent.objects.get_or_create(
                    event_id=e_data['event_id'],
                    defaults=e_data
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"  + Created Security Event: {obj.event_id} ({obj.get_event_type_display()})"))

        self.stdout.write(self.style.SUCCESS("All Hackathon FRS & Behavioral Demo Data Seeded Successfully!"))
