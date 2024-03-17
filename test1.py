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

# Send JSON payloads of varying sizes and measure the latency and throughput
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

            # resource monitoring
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            cpu_monitoring.append(cpu_percent)
            ram_monitoring.append(memory_percent)

        ws.close()
        results[test_case] = {"latency": latency_results, "throughput": throughput_results , "resource_monitoring": {"cpu": cpu_monitoring, "ram": ram_monitoring}}
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
        

def show_statistics(results):
    statistics = {}
    for test_case, metrics in results.items():
        print(f"Analysis for {test_case}:")
        
        # throughput 
        throughput_values = np.array(metrics['throughput'])
        throughput_mean = np.mean(throughput_values)
        cpu_monitoring_mean = np.mean(metrics['resource_monitoring']['cpu'])
        ram_monitoring_mean = np.mean(metrics['resource_monitoring']['ram'])
        
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
        cpu_data = metrics['resource_monitoring']['cpu']
        ram_data = metrics['resource_monitoring']['ram']
        time_points = range(len(cpu_data))
        plt.plot(time_points, cpu_data, label=f"{test_case} CPU Usage")
        plt.plot(time_points, ram_data, label=f"{test_case} RAM Usage")
    plt.xlabel('Time (seconds)')
    plt.ylabel('Usage (%)')
    plt.title('Resource Monitoring')
    plt.legend()
    plt.show(block=False)

# plot Throughput Statistics 
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

# plot Latency Statistics 
def plot_latancy_statics(results, payload_sizes):
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

    # URLs for the WebSocket servers
    urls = {"FastAPI": "ws://localhost:8000/ws", "aiohttp": "ws://localhost:8080/ws"}

    # Payload sizes to test
    payload_sizes = [1000, 5000, 10000, 20000, 50000, 60000, 70000, 80000, 90000, 100000]

    # Start resource monitoring in a separate thread to avoid blocking the main thread
    resource_monitoring_thread = threading.Thread(target=monitor_resource_usage, daemon=True)
    resource_monitoring_thread.start()

    # Run the tests
    results = run_tests(urls, payload_sizes, )

    show_statistics(results)

    # Plot resource usage
    plot_resource_usage(results)
    plot_throughput_statistics(results, payload_sizes)
    plot_latancy_statics(results, payload_sizes)