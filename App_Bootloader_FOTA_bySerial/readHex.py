import os


def parse_intel_hex_line(line):
    """Phân tích một dòng HEX theo chuẩn Intel HEX."""
    if not line.startswith(":"):
        return None

    try:
        line = line.strip()
        length = int(line[1:3], 16)
        address = int(line[3:7], 16)
        record_type = int(line[7:9], 16)
        data = [int(line[i:i+2], 16) for i in range(9, 9 + length * 2, 2)]
        checksum = int(line[9 + length * 2:11 + length * 2], 16)
        
        return {
            "length": length,
            "address": address,
            "type": record_type,
            "data": data,
            "checksum": checksum,
            "raw_line": line
        }
    except Exception as e:
        print(f"Lỗi dòng: {line.strip()} — {e}")
        return None

def parse_hex_file(file_path):
    """Đọc file HEX, lưu từng dòng hợp lệ vào list."""
    hex_lines = []

    with open(file_path, "r") as f:
        for line in f:
            parsed = parse_intel_hex_line(line)
            if parsed:
                hex_lines.append(parsed)

    return hex_lines
