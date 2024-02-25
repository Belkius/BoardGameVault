def item_header():
    return """
    <tr>
        <td>Name:</td>
        <td>Item ID:</td>
        <td>Type:</td>
        <td>Owned:</td>
        <td>Image:</td>
    </tr>
    """


def item(item):
    if item.thumbnail:
        thumbnail = item.thumbnail
    else:
        thumbnail = "http://localhost:8000/static/no_image.png"

    return f"""
    <tr>
        <td>{item.name}</td>
        <td>{item.item_id}</td>
        <td>{item.type}</td>
        <td>{item.owned}</td>
        <td><img src={thumbnail} alt={item.name}></td>
    </tr>
    """
