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

def test_parse_truecar_mi_and_pdk_automatic():
    html = """
    <div class="card">
      <h2>2010 Porsche Boxster</h2>
      <div class="price">$27,500</div>
      <div>87,345 mi • 7-Speed PDK Automatic</div>
    </div>
    """
    data = parse(html)
    assert data["year"] == 2010
    assert data["model"] == "Boxster"
    assert data["trim"] is None
    assert data["price"] == 27500
    assert data["miles"] == 87345
    assert data["transmission"] == "PDK"
def test_parse_truecar_vin_and_location():
    from x987.scrapers.truecar_com import parse
    html = """
    <div>
      <h1>2011 Porsche Cayman S</h1>
      <div class="price">$49,973</div>
      <div>71,161 miles • 7-Speed PDK Automatic</div>
      <div>VIN: WP0AB2A88BU780243 · Location: Denver, CO</div>
    </div>
    """
    data = parse(html)
    assert data["vin"] == "WP0AB2A88BU780243"
    assert data["location"] == "Denver, CO"
def test_parse_truecar_labeled_mileage_with_period():
    from x987.scrapers.truecar_com import parse
    html = """
    <div>
      <h1>2010 Porsche Boxster</h1>
      <div class="price">From $27,500</div>
      <div>Mileage: 87,345 mi.</div>
    </div>
    """
    data = parse(html)
    assert data["year"] == 2010
    assert data["model"] == "Boxster"
    assert data["price"] == 27500
    assert data["miles"] == 87345
def test_parse_truecar_tiptronic_maps_to_automatic():
    from x987.scrapers.truecar_com import parse
    html = """
    <div>
      <h1>2008 Porsche Cayman</h1>
      <div>$29,500</div>
      <div>65,100 miles • 5-Speed Tiptronic S</div>
    </div>
    """
    data = parse(html)
    assert data["year"] == 2008
    assert data["model"] == "Cayman"
    assert data["price"] == 29500
    assert data["miles"] == 65100
    assert data["transmission"] == "Automatic"
