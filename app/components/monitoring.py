import psutil
import GPUtil
import platform
import streamlit
import sys
from typing import Dict, Any

class SystemMonitor:
    """System monitoring and health checks"""
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # GPU information
        gpu_percent = None
        gpu_memory = None
        
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # First GPU
                gpu_percent = gpu.load * 100
                gpu_memory = (gpu.memoryUsed / gpu.memoryTotal) * 100
        except:
            pass
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used": memory.used / (1024**3),  # GB
            "memory_total": memory.total / (1024**3),  # GB
            "gpu_percent": gpu_percent,
            "gpu_memory": gpu_memory
        }
    
    def get_detailed_info(self) -> Dict[str, Any]:
        """Get detailed system information"""
        return {
            "python_version": platform.python_version(),
            "streamlit_version": streamlit.__version__,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cuda_available": self._check_cuda(),
            "gpu_count": len(GPUtil.getGPUs()) if GPUtil.getGPUs() else 0,
            "total_memory": psutil.virtual_memory().total / (1024**3),
            "available_storage": psutil.disk_usage('/').free / (1024**3)
        }
    
    def _check_cuda(self) -> bool:
        """Check if CUDA is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False