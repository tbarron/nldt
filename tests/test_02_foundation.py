import nldt
# -----------------------------------------------------------------------------
def test_clock():
    """
    nldt.clock() is an alias for time.clock()
    """
    pytest.debug_func()
    assert abs(nldt.clock() - time.clock()) < 0.0001


# -----------------------------------------------------------------------------
def test_utc_offset():
    """
    Check routine utc_offset() against some known timezones that don't change
    with dst
    """
    pytest.debug_func()
    m_dst_off = M("2001-01-01")
    m_dst_on = M("2001-07-01")
    assert nldt.utc_offset(tz='Singapore') == 8 * 3600

    assert nldt.utc_offset(m_dst_off.epoch(), tz='Pacific/Apia') == -11 * 3600
    assert nldt.utc_offset(m_dst_on.epoch(), tz='Pacific/Apia') == -11 * 3600

    # The expected value must be computed based on the local timezone, not
    # assumed to be Eastern.
    loc = get_localzone()
    exp_off = loc.utcoffset(datetime.fromtimestamp(m_dst_off.epoch()))
    exp_on = loc.utcoffset(datetime.fromtimestamp(m_dst_on.epoch()))
    assert nldt.utc_offset(m_dst_off.epoch()) == exp_off.total_seconds()
    assert nldt.utc_offset(m_dst_on.epoch()) == exp_on.total_seconds()

    # Note: we have to multiply time.{alt,time}zone by -1 here because the time
    # module, based on the Unix standard, assumes zones east of UTC have a
    # negative offset while those west of UTC have a positive offset. The UTC
    # standard defines this in the opposite way, assigning positive offsets to
    # the east and negative offsets to the west.
    #
    # With the UTC standard,
    #
    #      localtime = UTC + offset
    #      UTC = localtime - offset
    #
    # With the Unix standard,
    #
    #      localtime = UTC - offset
    #      UTC = localtime + offset
    #
    tm = time.localtime()
    if tm.tm_isdst:
        assert nldt.utc_offset() == -1 * time.altzone
    else:
        assert nldt.utc_offset() == -1 * time.timezone

    with pytest.raises(TypeError) as err:
        nldt.utc_offset(txt['nan'])
    assert txt['utc_offset'] in str(err)


# -----------------------------------------------------------------------------
def test_month_constructor():
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_month_days():
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_month_under_days():
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_month_index():
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_month_isleap():
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_month_names():
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_month_short_names():
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_month_match_monthnames():
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_week_constructor()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_week_day_list()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_week_find_day()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_week_forediff()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_week_backdiff()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_week_index()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_week_fullname()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_match_weekdays()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_day_number()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_tu_constructor()
    """
    Test class time_units constructor
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_tu_find_unit()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_tu_magnitude()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_tu_unit_list()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_caller_name()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_clock()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_local_constructor()
    """
    class local should have a constructor that accepts the name of a timezone,
    calls tzset(), and records the resulting values from
    time.{timezone,altzone,daylight,tzname}
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_local_timezone()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_local_altzone()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_local_daylight()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_local_tzname()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_dst()
@pytest.mark.parametrize("zname, std, soff, dst, doff", [
    pytest.param('US/Eastern', 'EST', 18000, 'EDT', 14400, id='est-edt'),
    pytest.param('US/Central', 'CST', 21600, 'CDT', 18000, id='csd-cdt'),
    pytest.param('US/Mountain', 'MST', 25200, 'MDT', 21600, id='mst-mdt'),
    pytest.param('US/Pacific', 'PST', 28800, 'PDT', 25200, id='pst-pdt'),
    pytest.param('Asia/Jakarta', 'WIB', -25200, 'WIB', -25200, id='wib'),
    ])
def test_tz_context_explicit(zname, std, soff, dst, doff):
    """
    Verify that 'with nldt.tz_context(FOOBAR)' creates a context with FOOBAR as
    the local timezone.
    """
    raise nldt.Stub()
    pytest.debug_func()
    with nldt.tz_context(zname):
        assert time.timezone == soff
        assert time.altzone == doff
        assert time.daylight == (soff != doff)
        assert time.tzname == (std, dst)


# -----------------------------------------------------------------------------
def test_timezone()
@pytest.mark.parametrize("zname", pytz.common_timezones)
def test_tz_context(zname):
    """
    Verify that 'with tz_context()' does the right thing for all timezones
    """
    raise nldt.Stub()
    pytest.debug_func()
    offl = nldt.offset_list(zname)
    assert 1 <= len(offl) <= 2
    if 1 == len(offl):
        exp_std = -1 * offl['std']['secs']
        exp_dst = exp_std
    else:
        exp_std = -1 * offl['std']['secs']
        exp_dst = -1 * offl['dst']['secs']
    with nldt.tz_context(zname):
        assert time.timezone == exp_std
        assert time.altzone == exp_dst
        assert time.daylight == (exp_std != exp_dst)


# -----------------------------------------------------------------------------
def test_timegm()
def test_tz_context_default():
    """
    Test default timezone context
    """
    raise nldt.Stub()
    pytest.debug_func()
    lz = get_localzone()
    std_dt = datetime(2011, 1, 1)
    std_offset = lz.utcoffset(std_dt).total_seconds()
    std_name = lz.tzname(std_dt)
    dst_dt = datetime(2011, 7, 1)
    dst_offset = lz.utcoffset(dst_dt).total_seconds()
    dst_name = lz.tzname(dst_dt)
    with nldt.tz_context():
        assert time.timezone == -1 * std_offset
        assert time.altzone == -1 * dst_offset
        assert time.daylight == (std_offset != dst_offset)
        assert time.tzname == (std_name, dst_name)


# -----------------------------------------------------------------------------
def test_tz_context()
def test_tz_context_nested():
    """
    Test nested timezone contexts
    """
    raise nldt.Stub()
    pytest.debug_func()
    with nldt.tz_context('Pacific/Honolulu'):
        assert time.timezone == 36000
        assert time.altzone == 36000
        assert time.daylight == 0
        assert time.tzname == ('HST', 'HST')
        with nldt.tz_context('US/Mountain'):
            assert time.timezone == 25200
            assert time.altzone == 21600
            assert time.daylight == 1
            assert time.tzname == ('MST', 'MDT')


# -----------------------------------------------------------------------------
def test_tzname()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_tzset()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_tzstring()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_word_before()
    """
    """
    raise nldt.Stub()



