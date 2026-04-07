import shutil


class ResourceMonitorService:
    def snapshot(self):
        memory = self._memory()
        disk = self._disk()
        return {
            "memory": memory,
            "disk": disk,
        }

    def _memory(self):
        try:
            import psutil  # type: ignore

            stats = psutil.virtual_memory()
            return {
                "total_mb": round(stats.total / (1024 * 1024), 2),
                "available_mb": round(stats.available / (1024 * 1024), 2),
                "percent_used": round(stats.percent, 2),
            }
        except Exception:
            return {
                "total_mb": None,
                "available_mb": None,
                "percent_used": None,
            }

    def _disk(self):
        usage = shutil.disk_usage(".")
        return {
            "total_gb": round(usage.total / (1024 * 1024 * 1024), 2),
            "free_gb": round(usage.free / (1024 * 1024 * 1024), 2),
            "used_gb": round(usage.used / (1024 * 1024 * 1024), 2),
        }
