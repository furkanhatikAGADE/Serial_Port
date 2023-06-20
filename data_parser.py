
def parse_data(data):
    if "sh_state :4" in data:
        values = data.split()
        return f"sh_state : ERROR"
    else:
        # print("parse_data unknow")
        return "Unknown data format"