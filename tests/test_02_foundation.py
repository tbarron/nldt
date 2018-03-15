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
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_timezone()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_timegm()
    """
    """
    raise nldt.Stub()


# -----------------------------------------------------------------------------
def test_tz_context()
    """
    """
    raise nldt.Stub()


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



