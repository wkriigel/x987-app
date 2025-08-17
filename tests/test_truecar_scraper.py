from x987.scrapers.truecar_com import parse

def test_parse_truecar_basic():
    html = """
    <html><body>
      <h1>2011 PORSCHE CAYMAN S</h1>
      <div class="price">Price: $49,973</div>
      <div class="meta">71,161 miles • 7-SPEED PDK AUTOMATIC • Rear Wheel Drive</div>
      <p>Features: BI-XENON HEADLIGHTS, SPORT CHRONO, 18" CAYMAN S WHEELS, HEATED SEATS</p>
    </body></html>
    """
    data = parse(html)
    assert data["year"] == 2011
    assert data["model"] == "Cayman"
    assert data["trim"] == "S"
    assert data["price"] == 49973
    assert data["miles"] == 71161
    assert data["transmission"] == "PDK"
