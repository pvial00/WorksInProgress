#!/usr/bin/env python


DB_HOST = 'mongo-datasync1.prod.pnap.ny.boinc'
DB_PORT = 27017
FAILOVER_RETRY_INTERVAL_SECS = 1
MAX_FAILOVER_RETRIES = 5
CONNECT_TIMEOUT_MS = 1000

DB_NAME = 'fschangelog'
COLLECTION_NAME = 'deltas'
POOL_COLLECTION_NAME = 'segment_pools'
