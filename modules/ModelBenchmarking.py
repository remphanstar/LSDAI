# Model Performance Benchmarking and Testing Suite
# Save as: modules/ModelBenchmarking.py

import json_utils as js
from pathlib import Path
import subprocess
import threading
import requests
import hashlib
import sqlite3
import base64
import psutil
import time
import json
import os
import re
from datetime import datetime
from PIL import Image, ImageStat
import numpy as np
from typing import Dict, List, Any, Optional

class BenchmarkTest:
    """Individual benchmark test configuration"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.results = {}
        
    def get_prompt(self) -> str:
        return self.config.get('prompt', 'a beautiful landscape')
        
    def get_settings(self) -> Dict[str, Any]:
        return self.config.get('settings', {})
        
    def get_expected_results(self) -> Dict[str, Any]:
        return self.config.get('expected_results', {})

class ModelBenchmarkSuite:
    """Comprehensive model benchmarking suite"""
    
    def __init__(self, webui_api_url='http://127.0.0.1:7860'):
        self.api_url = webui_api_url.rstrip('/')
        self.results_db = self._init_database()
        self.benchmark_tests = self._load_benchmark_tests()
        self.current_session = None
        
    def _init_database(self):
        """Initialize benchmark results database"""
        db_path = Path('data/benchmark_results.db')
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS benchmark_sessions (
                    session_id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    system_specs TEXT,
                    notes TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS model_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    generation_time REAL,
                    memory_usage REAL,
                    gpu_usage REAL,
                    image_quality_score REAL,
                    prompt_adherence_score REAL,
                    technical_quality TEXT,
                    settings TEXT,
                    image_path TEXT,
                    timestamp REAL NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES benchmark_sessions(session_id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id INTEGER NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (test_id) REFERENCES model_tests(id)
                )
            ''')
            
        return db_path
        
    def _load_benchmark_tests(self):
        """Load benchmark test configurations"""
        default_tests = {
            'quality_test': BenchmarkTest('Quality Test', {
                'prompt': 'a photorealistic portrait of a woman with brown hair, professional lighting, 4k, detailed',
                'settings': {
                    'steps': 50,
                    'cfg_scale': 7.5,
                    'width': 512,
                    'height': 512,
                    'sampler_name': 'DPM++ 2M Karras'
                },
                'expected_results': {
                    'min_quality_score': 0.7,
                    'max_generation_time': 60
                }
            }),
            'speed_test': BenchmarkTest('Speed Test', {
                'prompt': 'a simple landscape with mountains and trees',
                'settings': {
                    'steps': 20,
                    'cfg_scale': 7.0,
                    'width': 512,
                    'height': 512,
                    'sampler_name': 'Euler a'
                },
                'expected_results': {
                    'max_generation_time': 30
                }
            }),
            'memory_test': BenchmarkTest('Memory Efficiency Test', {
                'prompt': 'a detailed cityscape at night with lights and reflections',
                'settings': {
                    'steps': 30,
                    'cfg_scale': 8.0,
                    'width': 768,
                    'height': 768,
                    'sampler_name': 'DPM++ SDE Karras'
                },
                'expected_results': {
                    'max_memory_usage': 8000  # MB
                }
            }),
            'consistency_test': BenchmarkTest('Consistency Test', {
                'prompt': 'a red apple on a wooden table, studio lighting',
                'settings': {
                    'steps': 25,
                    'cfg_scale': 7.0,
                    'width': 512,
                    'height': 512,
                    'sampler_name': 'DPM++ 2M',
                    'seed': 42  # Fixed seed for consistency
                },
                'expected_results': {
                    'consistency_threshold': 0.9
                }
            }),
            'style_test': BenchmarkTest('Style Adherence Test', {
                'prompt': 'an anime girl with blue hair, manga style, cel shading',
                'settings': {
                    'steps': 35,
                    'cfg_scale': 9.0,
                    'width': 512,
                    'height': 768,
                    'sampler_name': 'DPM++ 2M Karras'
                },
                'expected_results': {
                    'style_score_threshold': 0.8
                }
            })
        }
        
        # Load custom tests if available
        custom_tests_file = Path('data/custom_benchmark_tests.json')
        if custom_tests_file.exists():
            try:
                with open(custom_tests_file, 'r') as f:
                    custom_configs = json.load(f)
                    for name, config in custom_configs.items():
                        default_tests[name] = BenchmarkTest(name, config)
            except Exception as e:
                print(f"Error loading custom benchmark tests: {e}")
                
        return default_tests
        
    def start_benchmark_session(self, notes: str = ""):
        """Start a new benchmark session"""
        self.current_session = f"session_{int(time.time())}"
        
        # Collect system specs
        system_specs = {
            'cpu': {
                'count': psutil.cpu_count(),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            'memory': {
                'total_gb': psutil.virtual_memory().total / (1024**3)
            },
            'gpu': self._get_gpu_specs(),
            'platform': os.name,
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        }
        
        with sqlite3.connect(self.results_db) as conn:
            conn.execute('''
                INSERT INTO benchmark_sessions (session_id, timestamp, system_specs, notes)
                VALUES (?, ?, ?, ?)
            ''', (
                self.current_session,
                time.time(),
                json.dumps(system_specs),
                notes
            ))
            
        print(f"🚀 Started benchmark session: {self.current_session}")
        return self.current_session
        
    def _get_gpu_specs(self):
        """Get GPU specifications"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                return {
                    'name': gpu.name,
                    'memory_total_mb': gpu.memoryTotal,
                    'driver': gpu.driver
                }
        except ImportError:
            pass
            
        return None
        
    def benchmark_model(self, model_name: str, test_names: List[str] = None) -> Dict[str, Any]:
        """Benchmark a specific model with selected tests"""
        if not self.current_session:
            self.start_benchmark_session()
            
        if test_names is None:
            test_names = list(self.benchmark_tests.keys())
            
        print(f"🔬 Benchmarking model: {model_name}")
        print(f"📋 Tests to run: {', '.join(test_names)}")
        
        # Switch to the model
        if not self._switch_model(model_name):
            print(f"❌ Failed to switch to model: {model_name}")
            return {}
            
        results = {}
        
        for test_name in test_names:
            if test_name not in self.benchmark_tests:
                print(f"⚠️  Unknown test: {test_name}")
                continue
                
            print(f"🧪 Running test: {test_name}")
            test_result = self._run_test(model_name, self.benchmark_tests[test_name])
            results[test_name] = test_result
            
            # Save result to database
            self._save_test_result(model_name, test_name, test_result)
            
        print(f"✅ Benchmark completed for {model_name}")
        return results
        
    def _switch_model(self, model_name: str) -> bool:
        """Switch to specified model via API"""
        try:
            # Get current model
            response = requests.get(f"{self.api_url}/sdapi/v1/options")
            if response.status_code != 200:
                return False
                
            current_options = response.json()
            
            # Set new model
            new_options = {"sd_model_checkpoint": model_name}
            response = requests.post(f"{self.api_url}/sdapi/v1/options", json=new_options)
            
            if response.status_code == 200:
                # Wait for model to load
                time.sleep(10)
                return True
                
        except Exception as e:
            print(f"Error switching model: {e}")
            
        return False
        
    def _run_test(self, model_name: str, test: BenchmarkTest) -> Dict[str, Any]:
        """Run individual benchmark test"""
        start_time = time.time()
        
        # Get initial system state
        initial_memory = psutil.virtual_memory().used
        initial_gpu_memory = self._get_gpu_memory_usage()
        
        try:
            # Prepare generation request
            payload = {
                "prompt": test.get_prompt(),
                "steps": test.get_settings().get('steps', 20),
                "cfg_scale": test.get_settings().get('cfg_scale', 7.0),
                "width": test.get_settings().get('width', 512),
                "height": test.get_settings().get('height', 512),
                "sampler_name": test.get_settings().get('sampler_name', 'Euler a'),
                "seed": test.get_settings().get('seed', -1),
                "batch_size": 1,
                "n_iter": 1
            }
            
            # Generate image
            response = requests.post(f"{self.api_url}/sdapi/v1/txt2img", json=payload)
            
            generation_time = time.time() - start_time
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f"API error: {response.status_code}",
                    'generation_time': generation_time
                }
                
            result_data = response.json()
            
            # Get final system state
            final_memory = psutil.virtual_memory().used
            final_gpu_memory = self._get_gpu_memory_usage()
            
            memory_usage = (final_memory - initial_memory) / (1024 * 1024)  # MB
            gpu_memory_usage = (final_gpu_memory - initial_gpu_memory) if initial_gpu_memory and final_gpu_memory else 0
            
            # Save and analyze generated image
            image_path = self._save_generated_image(model_name, test.name, result_data['images'][0])
            quality_metrics = self._analyze_image_quality(image_path, test)
            
            return {
                'success': True,
                'generation_time': generation_time,
                'memory_usage': memory_usage,
                'gpu_memory_usage': gpu_memory_usage,
                'image_path': str(image_path),
                'quality_metrics': quality_metrics,
                'settings': test.get_settings(),
                'prompt': test.get_prompt()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'generation_time': time.time() - start_time
            }
            
    def _get_gpu_memory_usage(self) -> Optional[float]:
        """Get current GPU memory usage in MB"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                return gpus[0].memoryUsed
        except ImportError:
            pass
        return None
        
    def _save_generated_image(self, model_name: str, test_name: str, image_b64: str) -> Path:
        """Save generated image to disk"""
        # Create directory structure
        output_dir = Path('benchmark_results') / self.current_session / model_name.replace(' ', '_')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Decode and save image
        image_data = base64.b64decode(image_b64)
        timestamp = int(time.time())
        image_path = output_dir / f"{test_name}_{timestamp}.png"
        
        with open(image_path, 'wb') as f:
            f.write(image_data)
            
        return image_path
        
    def _analyze_image_quality(self, image_path: Path, test: BenchmarkTest) -> Dict[str, float]:
        """Analyze generated image quality"""
        try:
            image = Image.open(image_path)
            
            # Basic quality metrics
            metrics = {}
            
            # Sharpness (Laplacian variance)
            metrics['sharpness'] = self._calculate_sharpness(image)
            
            # Contrast
            metrics['contrast'] = self._calculate_contrast(image)
            
            # Color diversity
            metrics['color_diversity'] = self._calculate_color_diversity(image)
            
            # Brightness distribution
            metrics['brightness_std'] = self._calculate_brightness_std(image)
            
            # Noise level
            metrics['noise_level'] = self._calculate_noise_level(image)
            
            # Overall quality score (weighted combination)
            metrics['overall_quality'] = self._calculate_overall_quality(metrics)
            
            return metrics
            
        except Exception as e:
            print(f"Error analyzing image quality: {e}")
            return {}
            
    def _calculate_sharpness(self, image: Image.Image) -> float:
        """Calculate image sharpness using Laplacian variance"""
        try:
            import cv2
            
            # Convert to grayscale
            gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # Calculate Laplacian variance
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            return float(laplacian.var())
            
        except ImportError:
            # Fallback method without OpenCV
            gray = image.convert('L')
            array = np.array(gray)
            
            # Simple edge detection
            sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
            sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
            
            edges_x = np.abs(np.convolve(array.flatten(), sobel_x.flatten(), mode='same'))
            edges_y = np.abs(np.convolve(array.flatten(), sobel_y.flatten(), mode='same'))
            
            return float(np.mean(edges_x + edges_y))
            
    def _calculate_contrast(self, image: Image.Image) -> float:
        """Calculate image contrast"""
        gray = image.convert('L')
        stat = ImageStat.Stat(gray)
        return stat.stddev[0]
        
    def _calculate_color_diversity(self, image: Image.Image) -> float:
        """Calculate color diversity"""
        # Get unique colors
        colors = image.getcolors(maxcolors=256*256*256)
        if colors:
            unique_colors = len(colors)
            total_pixels = image.width * image.height
            return unique_colors / total_pixels
        return 0.0
        
    def _calculate_brightness_std(self, image: Image.Image) -> float:
        """Calculate brightness standard deviation"""
        gray = image.convert('L')
        stat = ImageStat.Stat(gray)
        return stat.stddev[0]
        
    def _calculate_noise_level(self, image: Image.Image) -> float:
        """Estimate noise level in image"""
        array = np.array(image.convert('L'))
        
        # Use high-pass filter to detect noise
        kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        filtered = np.abs(np.convolve(array.flatten(), kernel.flatten(), mode='same'))
        
        return float(np.mean(filtered))
        
    def _calculate_overall_quality(self, metrics: Dict[str, float]) -> float:
        """Calculate overall quality score from individual metrics"""
        if not metrics:
            return 0.0
            
        # Normalize and weight metrics
        normalized_sharpness = min(metrics.get('sharpness', 0) / 1000, 1.0)
        normalized_contrast = min(metrics.get('contrast', 0) / 100, 1.0)
        normalized_diversity = metrics.get('color_diversity', 0)
        
        # Weighted average
        quality_score = (
            normalized_sharpness * 0.3 +
            normalized_contrast * 0.3 +
            normalized_diversity * 0.2 +
            (1.0 - min(metrics.get('noise_level', 0) / 1000, 1.0)) * 0.2
        )
        
        return float(quality_score)
        
    def _save_test_result(self, model_name: str, test_name: str, result: Dict[str, Any]):
        """Save test result to database"""
        with sqlite3.connect(self.results_db) as conn:
            cursor = conn.execute('''
                INSERT INTO model_tests 
                (session_id, model_name, test_name, generation_time, memory_usage, 
                 gpu_usage, image_quality_score, settings, image_path, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.current_session,
                model_name,
                test_name,
                result.get('generation_time'),
                result.get('memory_usage'),
                result.get('gpu_memory_usage'),
                result.get('quality_metrics', {}).get('overall_quality'),
                json.dumps(result.get('settings', {})),
                result.get('image_path'),
                time.time()
            ))
            
            test_id = cursor.lastrowid
            
            # Save quality metrics
            quality_metrics = result.get('quality_metrics', {})
            for metric_name, metric_value in quality_metrics.items():
                conn.execute('''
                    INSERT INTO quality_metrics (test_id, metric_name, metric_value)
                    VALUES (?, ?, ?)
                ''', (test_id, metric_name, metric_value))
                
    def compare_models(self, model_names: List[str], test_names: List[str] = None) -> Dict[str, Any]:
        """Compare multiple models across benchmark tests"""
        if not self.current_session:
            self.start_benchmark_session("Model Comparison")
            
        comparison_results = {}
        
        for model_name in model_names:
            print(f"\n🔬 Benchmarking {model_name}...")
            comparison_results[model_name] = self.benchmark_model(model_name, test_names)
            
        # Generate comparison report
        report = self._generate_comparison_report(comparison_results)
        
        # Save comparison report
        self._save_comparison_report(report)
        
        return report
        
    def _generate_comparison_report(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comparison report from benchmark results"""
        report = {
            'session_id': self.current_session,
            'timestamp': time.time(),
            'models_tested': list(results.keys()),
            'summary': {},
            'detailed_results': results,
            'rankings': {}
        }
        
        # Calculate averages and rankings for each metric
        metrics_to_rank = ['generation_time', 'memory_usage', 'overall_quality']
        
        for metric in metrics_to_rank:
            model_scores = {}
            
            for model_name, model_results in results.items():
                scores = []
                for test_name, test_result in model_results.items():
                    if test_result.get('success'):
                        if metric == 'overall_quality':
                            score = test_result.get('quality_metrics', {}).get('overall_quality', 0)
                        else:
                            score = test_result.get(metric, 0)
                        scores.append(score)
                        
                if scores:
                    model_scores[model_name] = sum(scores) / len(scores)
                    
            # Rank models (lower is better for time/memory, higher for quality)
            if metric in ['generation_time', 'memory_usage']:
                ranked = sorted(model_scores.items(), key=lambda x: x[1])
            else:
                ranked = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
                
            report['rankings'][metric] = ranked
            report['summary'][metric] = model_scores
            
        return report
        
    def _save_comparison_report(self, report: Dict[str, Any]):
        """Save comparison report to file"""
        reports_dir = Path('benchmark_results') / self.current_session
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / 'comparison_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"📊 Comparison report saved: {report_file}")
        
    def get_model_performance_history(self, model_name: str, days: int = 30) -> Dict[str, Any]:
        """Get performance history for a model"""
        since_timestamp = time.time() - (days * 24 * 3600)
        
        with sqlite3.connect(self.results_db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM model_tests 
                WHERE model_name = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            ''', (model_name, since_timestamp))
            
            results = [dict(row) for row in cursor.fetchall()]
            
        # Organize by test type
        history = {}
        for result in results:
            test_name = result['test_name']
            if test_name not in history:
                history[test_name] = []
            history[test_name].append(result)
            
        return history
        
    def export_benchmark_data(self, session_id: str = None, output_path: str = None):
        """Export benchmark data to JSON file"""
        if session_id is None:
            session_id = self.current_session
            
        if output_path is None:
            output_path = f"benchmark_export_{session_id}.json"
            
        with sqlite3.connect(self.results_db) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get session info
            session_cursor = conn.execute(
                "SELECT * FROM benchmark_sessions WHERE session_id = ?",
                (session_id,)
            )
            session_data = dict(session_cursor.fetchone())
            
            # Get test results
            tests_cursor = conn.execute(
                "SELECT * FROM model_tests WHERE session_id = ?",
                (session_id,)
            )
            test_results = [dict(row) for row in tests_cursor.fetchall()]
            
            # Get quality metrics
            for test in test_results:
                metrics_cursor = conn.execute(
                    "SELECT * FROM quality_metrics WHERE test_id = ?",
                    (test['id'],)
                )
                test['quality_metrics'] = [dict(row) for row in metrics_cursor.fetchall()]
                
        export_data = {
            'session': session_data,
            'test_results': test_results,
            'export_timestamp': time.time()
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        print(f"📁 Benchmark data exported: {output_path}")

# Global benchmark suite instance
benchmark_suite = None

def get_benchmark_suite():
    """Get or create benchmark suite instance"""
    global benchmark_suite
    
    if benchmark_suite is None:
        benchmark_suite = ModelBenchmarkSuite()
        
    return benchmark_suite

def quick_model_comparison(model_names: List[str], tests: List[str] = None):
    """Quick function to compare models"""
    suite = get_benchmark_suite()
    
    if tests is None:
        tests = ['speed_test', 'quality_test', 'memory_test']
        
    return suite.compare_models(model_names, tests)

def benchmark_current_model(test_name: str = 'quality_test'):
    """Benchmark the currently loaded model"""
    suite = get_benchmark_suite()
    
    # Get current model name from API
    try:
        response = requests.get(f"{suite.api_url}/sdapi/v1/options")
        if response.status_code == 200:
            current_model = response.json().get('sd_model_checkpoint', 'unknown')
            return suite.benchmark_model(current_model, [test_name])
    except Exception as e:
        print(f"Error getting current model: {e}")
        
    return {}

print("Model Performance Benchmarking and Testing Suite loaded!")
