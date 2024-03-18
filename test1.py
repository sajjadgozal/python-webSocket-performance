from websocket import create_connection
import time
import json
import numpy as np
import psutil
import threading
import matplotlib.pyplot as plt

def send_json_payload(ws, payload="hello"):
    start_time = time.time()
    ws.send(json.dumps(payload).encode())
    latency = time.time() - start_time
    return latency

def run_tests(urls, payload_sizes):
    results = {}
    for test_case, url in urls.items():
        ws = create_connection(url)
        print(f"Testing {test_case}...")

        latency_results = []
        throughput_results = []
        cpu_monitoring = []
        ram_monitoring = []

        for size in payload_sizes:
            payload = {"data": "x" * size}
            latency = send_json_payload(ws, payload)
            throughput = size / latency
            latency_results.append(latency)
            throughput_results.append(throughput)

            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            cpu_monitoring.append(cpu_percent)
            ram_monitoring.append(memory_percent)

        ws.close()
        results[test_case] = {
            "latency": latency_results,
            "throughput": throughput_results,
            "cpu": cpu_monitoring,
            "ram": ram_monitoring
        }
    return results
    
def monitor_resource_usage():
    cpu_monitoring = []
    ram_monitoring = []
    while True:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        cpu_monitoring.append(cpu_percent)
        ram_monitoring.append(memory_percent)
        time.sleep(1)

def sample_mean(data):
    result = {}
    for item in data:
        for key in item:
            result.setdefault(key, {})
            for inner_key, inner_value in item[key].items():
                result[key].setdefault(inner_key, [])
                if isinstance(inner_value, list):
                    result[key][inner_key] = [(a + b) / 2 for a, b in zip(result[key][inner_key], inner_value)] if result[key][inner_key] else inner_value
    return result
        
def show_statistics(results):
    statistics = {}
    for test_case, metrics in results.items():
        print(f"Analysis for {test_case}:")
        
        throughput_mean = np.mean(metrics['throughput'])
        cpu_monitoring_mean = np.mean(metrics['cpu'])
        ram_monitoring_mean = np.mean(metrics['ram'])
        
        statistics[test_case] = {
            'throughput_mean': throughput_mean,
            'cpu_monitoring_mean': cpu_monitoring_mean,
            'ram_monitoring_mean': ram_monitoring_mean
        }
        
        print("Throughput Statistics:")
        print(f"  Mean: {throughput_mean:.2f} bytes/second")
        print(f"  CPU Monitoring Mean: {cpu_monitoring_mean:.2f}%")
        print(f"  RAM Monitoring Mean: {ram_monitoring_mean:.2f}%")

def plot_resource_usage(results):
    plt.figure()

    for test_case, metrics in results.items():
        cpu_data = metrics['cpu']
        ram_data = metrics['ram']
        time_points = range(len(cpu_data))
        plt.plot(time_points, cpu_data, label=f"{test_case} CPU Usage")
        plt.plot(time_points, ram_data, label=f"{test_case} RAM Usage")
    plt.xlabel('Time (seconds)')
    plt.ylabel('Usage (%)')
    plt.title('Resource Monitoring')
    plt.legend()
    plt.show(block=False)

def plot_throughput_statistics(results, payload_sizes):
    plt.figure()
    for test_case, metrics in results.items():
        throughput = metrics['throughput']
        plt.plot(payload_sizes, throughput, label=test_case)
    plt.xlabel('Payload Size (bytes)')
    plt.ylabel('Throughput (bytes/second)')
    plt.title('Throughput Statistics')
    plt.legend()
    plt.show(block=False)

def plot_latency_statistics(results, payload_sizes):
    plt.figure()
    for test_case, metrics in results.items():
        latency = metrics['latency']
        plt.plot(payload_sizes, latency, label=test_case)
    plt.xlabel('Payload Size (bytes)')
    plt.ylabel('Latency (bytes/second)')
    plt.title('Latency Statistics')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    urls = {
        "FastAPI": "ws://localhost:8000/ws",
        "aiohttp": "ws://localhost:8080/ws"
    }

    payload_sizes = [500, 1000, 10000, 30000, 50000, 100000]
    sample_count = 1

    resource_monitoring_thread = threading.Thread(target=monitor_resource_usage, daemon=True)
    resource_monitoring_thread.start()

    all_results = []
    for _ in range(sample_count):
        all_results.append(run_tests(urls, payload_sizes))
    results = sample_mean(all_results)

    # print(results)

    show_statistics(results)
    plot_resource_usage(results)
    plot_throughput_statistics(results, payload_sizes)
    plot_latency_statistics(results, payload_sizes)
