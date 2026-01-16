import json
import os

def translate_dashboard(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Translation mapping for common Grafana dashboard terms
    translation_map = {
        # Titles
        "Quick CPU / Mem / Disk": "핵심 지표 요약 (CPU / 메모리 / 디스크)",
        "Pressure": "리소스 부하 상태 (Pressure)",
        "CPU Busy": "CPU 사용률",
        "Sys Load": "시스템 부하 (Load)",
        "RAM Used": "메모리 사용량 (RAM)",
        "SWAP Used": "스왑 사용량 (SWAP)",
        "Root FS Used": "루트 디스크 사용량",
        "CPU Cores": "CPU 코어 수",
        "RAM Total": "전체 메모리 용량",
        "SWAP Total": "전체 스왑 용량",
        "RootFS Total": "전체 디스크 용량",
        "Uptime": "서버 가동 시간 (Uptime)",
        "Basic CPU / Mem / Net / Disk": "기본 리소스 현황 (CPU / 메모리 / 네트워크 / 디스크)",
        "CPU Basic": "기본 CPU 상태",
        "Memory Basic": "기본 메모리 상태",
        "Network Traffic Basic": "네트워크 트래픽 (기본)",
        "Disk Space Used Basic": "디스크 사용량 (기본)",
        "CPU / Memory / Net / Disk": "리소스 상세 현황 (CPU / 메모리 / 네트워크 / 디스크)",
        "Disk IOps": "디스크 I/O 횟수 (IOPS)",
        "Disk Throughput": "디스크 전송 속도 (Throughput)",
        "Filesystem Space Available": "파일시스템 남은 용량",
        "Filesystem Used": "파일시스템 사용량",
        "Disk I/O Utilization": "디스크 I/O 사용률",
        "Pressure Stall Information": "리소스 지연 정보 (PSI)",
        "Memory Committed": "할당된 메모리 (Committed)",
        "Memory Writeback and Dirty": "디스크 쓰기 대기 메모리 (Dirty/Writeback)",
        "Memory Slab": "커널 슬랩 메모리 (Slab)",
        "Memory Shared and Mapped": "공유 및 매핑된 메모리",
        "Memory LRU Active / Inactive (%)": "메모리 활성/비활성 비율 (LRU)",
        "Memory LRU Active / Inactive Detail": "메모리 활성/비활성 상세",
        "Processes": "프로세스 현황",
        "Context Switches": "컨텍스트 스위칭",
        "Interrupts": "인터럽트",
        "Network Traffic": "네트워크 트래픽 상세",
        "Network Saturation": "네트워크 포화도",
        "Network Errors / Drops": "네트워크 에러 / 드롭",
        
        # Legend Formats / Labels
        "Used": "사용 중",
        "Free": "여유 공간",
        "Total": "전체",
        "Idle": "유휴 (Idle)",
        "System": "시스템 (System)",
        "User": "사용자 (User)",
        "Iowait": "I/O 대기 (Iowait)",
        "Steal": "가상화 손실 (Steal)",
        "Nice": "우선순위 변경 (Nice)",
        "Softirq": "소프트 인터럽트 (Softirq)",
        "Irq": "인터럽트 (Irq)",
        "Cache + Buffer": "캐시 + 버퍼",
        "Swap used": "스왑 사용량",
        "Apps": "애플리케이션",
    }

    # Technical descriptions (Beginner-friendly)
    description_map = {
        "Resource pressure via PSI": "리눅스 PSI(Pressure Stall Information)를 통한 CPU/메모리/IO 부하 상태입니다.",
        "Overall CPU busy percentage (averaged across all cores)": "모든 CPU 코어의 평균 사용률입니다.",
        "System load  over all CPU cores together": "시스템의 전반적인 작업 부하 지수입니다.",
        "Real RAM usage excluding cache and reclaimable memory": "캐시와 버퍼를 제외한 실제 애플리케이션 등이 사용하는 메모리량입니다.",
        "Percentage of swap space currently used by the system": "물리 메모리 부족 시 사용하는 스왑 영역의 사용 비율입니다.",
        "Used Root FS": "루트 파일 시스템(/)의 사용량입니다.",
        "CPU time spent busy vs idle, split by activity type": "CPU가 어떤 작업(사용자 프로그램, 시스템 등)에 시간을 쓰고 있는지 보여줍니다.",
        "RAM and swap usage overview, including caches": "전체 메모리와 스왑 메모리의 사용 현황입니다. 캐시 영역도 포함됩니다.",
        "Per-interface network traffic (receive and transmit) in bits per second": "네트워크 카드별 수신(Rx) 및 송신(Tx) 트래픽량입니다.",
        "Percentage of filesystem space used for each mounted device": "연결된 디스크(마운트 지점)별 사용량 비율입니다.",
    }

    def walk(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "title" and isinstance(v, str):
                    # Match full title or replace parts
                    if v in translation_map:
                        obj[k] = translation_map[v]
                    else:
                        # Try partial replacement for things like "Rx {{device}}"
                        new_v = v
                        if "Rx" in v: new_v = new_v.replace("Rx", "수신 (Rx)")
                        if "Tx" in v: new_v = new_v.replace("Tx", "송신 (Tx)")
                        if "Read" in v: new_v = new_v.replace("Read", "읽기")
                        if "Write" in v: new_v = new_v.replace("Write", "쓰기")
                        obj[k] = new_v
                
                elif k == "description" and isinstance(v, str):
                    if v in description_map:
                        obj[k] = description_map[v]
                
                elif k == "legendFormat" and isinstance(v, str):
                    if v in translation_map:
                        obj[k] = translation_map[v]
                    else:
                        new_v = v
                        if "Rx" in v: new_v = new_v.replace("Rx", "수신 (Rx)")
                        if "Tx" in v: new_v = new_v.replace("Tx", "송신 (Tx)")
                        obj[k] = new_v
                
                walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(data)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    translate_dashboard(
        "./dash_board.json",
        "./dash_board_ko.json"
    )
    print("Translation completed: dash_board_ko.json")
