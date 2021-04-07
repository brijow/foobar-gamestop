from joblib import Parallel, delayed

from wsb_comments_producer import comments_monitor
from wsb_submissions_producer import submissions_monitor

Parallel(n_jobs=2)(delayed(func)(1) for func in [comments_monitor, submissions_monitor])