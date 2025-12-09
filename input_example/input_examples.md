# CoderEval Input Example

```
def _run_playbook(cli_args, vars_dict, ir_workspace, ir_plugin):
	"""
	Runs ansible cli with vars dict
        :param vars_dict: dict, Will be passed as Ansible extra-vars
        :param cli_args: the list  of command line arguments
        :param ir_workspace: An Infrared Workspace object represents the active
         workspace
        :param ir_plugin: An InfraredPlugin object of the current plugin
        :return: ansible results
	"""
```

# SWE-bench-NF Input Example

```
You will be provided with a partial code base and an issue statement explaining a problem to resolve.
<issue>
Support "%V" format in WeekArchiveView.
Description
	
#26217 (Docs for WeekArchiveView are misleading about %W) - closed 4 years ago mentioned support for %V week format.
Since python 3.6, %G, %u and %V ISO 8601 formatters were added to strptime.
WeekArchiveView should add %V to the list of accepted week formatters. This would require as well the special case to change the year format to %G, or simply ValueError in _date_from_string should mention the message passed from datetime.datetime.strptime:
ISO week directive '%V' is incompatible with the year directive '%Y'. Use the ISO year '%G'.

</issue>
<code>
[start of README.rst]
1 ======
2 Django
3 ======
4 
5 Django is a high-level Python Web framework that encourages rapid development
6 and clean, pragmatic design. Thanks for checking it out.
7 
8 All documentation is in the "``docs``" directory and online at
9 https://docs.djangoproject.com/en/stable/. If you're just getting started,
10 here's how we recommend you read the docs:
11 
12 * First, read ``docs/intro/install.txt`` for instructions on installing Django.
13 
14 * Next, work through the tutorials in order (``docs/intro/tutorial01.txt``,
15   ``docs/intro/tutorial02.txt``, etc.).
16 
17 * If you want to set up an actual deployment server, read
18   ``docs/howto/deployment/index.txt`` for instructions.
19 
20 * You'll probably want to read through the topical guides (in ``docs/topics``)
21   next; from there you can jump to the HOWTOs (in ``docs/howto``) for specific
22   problems, and check out the reference (``docs/ref``) for gory details.
23 
24 * See ``docs/README`` for instructions on building an HTML version of the docs.
25 
26 Docs are updated rigorously. If you find any problems in the docs, or think
27 they should be clarified in any way, please take 30 seconds to fill out a
28 ticket here: https://code.djangoproject.com/newticket
29 
30 To get more help:
31 
32 * Join the ``#django`` channel on irc.freenode.net. Lots of helpful people hang
33   out there. See https://freenode.net/kb/answer/chat if you're new to IRC.
34 
35 * Join the django-users mailing list, or read the archives, at
36   https://groups.google.com/group/django-users.
37 
38 To contribute to Django:
39 
40 * Check out https://docs.djangoproject.com/en/dev/internals/contributing/ for
41   information about getting involved.
42 
43 To run Django's test suite:
44 
45 * Follow the instructions in the "Unit tests" section of
46   ``docs/internals/contributing/writing-code/unit-tests.txt``, published online at
47   https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/unit-tests/#running-the-unit-tests
48 
[end of README.rst]
[start of django/utils/dateformat.py]
1 """
2 PHP date() style date formatting
3 See http://www.php.net/date for format strings
4 
5 Usage:
6 >>> import datetime
7 >>> d = datetime.datetime.now()
8 >>> df = DateFormat(d)
9 >>> print(df.format('jS F Y H:i'))
10 7th October 2003 11:39
11 >>>
12 """
13 import calendar
14 import datetime
15 import time
16 from email.utils import format_datetime as format_datetime_rfc5322
17 
18 from django.utils.dates import (
19     MONTHS, MONTHS_3, MONTHS_ALT, MONTHS_AP, WEEKDAYS, WEEKDAYS_ABBR,
20 )
21 from django.utils.regex_helper import _lazy_re_compile
22 from django.utils.timezone import (
23     get_default_timezone, is_aware, is_naive, make_aware,
24 )
25 from django.utils.translation import gettext as _
26 
27 re_formatchars = _lazy_re_compile(r'(?<!\\)([aAbcdDeEfFgGhHiIjlLmMnNoOPrsStTUuwWyYzZ])')
28 re_escaped = _lazy_re_compile(r'\\(.)')
29 
30 
31 class Formatter:
32     def format(self, formatstr):
33         pieces = []
34         for i, piece in enumerate(re_formatchars.split(str(formatstr))):
35             if i % 2:
36                 if type(self.data) is datetime.date and hasattr(TimeFormat, piece):
37                     raise TypeError(
38                         "The format for date objects may not contain "
39                         "time-related format specifiers (found '%s')." % piece
40                     )
41                 pieces.append(str(getattr(self, piece)()))
42             elif piece:
43                 pieces.append(re_escaped.sub(r'\1', piece))
44         return ''.join(pieces)
45 
46 
47 class TimeFormat(Formatter):
48 
49     def __init__(self, obj):
50         self.data = obj
51         self.timezone = None
52 
53         # We only support timezone when formatting datetime objects,
54         # not date objects (timezone information not appropriate),
55         # or time objects (against established django policy).
56         if isinstance(obj, datetime.datetime):
57             if is_naive(obj):
58                 self.timezone = get_default_timezone()
59             else:
60                 self.timezone = obj.tzinfo
61 
62     def a(self):
63         "'a.m.' or 'p.m.'"
64         if self.data.hour > 11:
65             return _('p.m.')
66         return _('a.m.')
67 
68     def A(self):
69         "'AM' or 'PM'"
70         if self.data.hour > 11:
71             return _('PM')
72         return _('AM')
73 
74     def e(self):
75         """
76         Timezone name.
77 
78         If timezone information is not available, return an empty string.
79         """
80         if not self.timezone:
81             return ""
82 
83         try:
84             if hasattr(self.data, 'tzinfo') and self.data.tzinfo:
85                 return self.data.tzname() or ''
86         except NotImplementedError:
87             pass
88         return ""
89 
90     def f(self):
91         """
92         Time, in 12-hour hours and minutes, with minutes left off if they're
93         zero.
94         Examples: '1', '1:30', '2:05', '2'
95         Proprietary extension.
96         """
97         if self.data.minute == 0:
98             return self.g()
99         return '%s:%s' % (self.g(), self.i())
100 
101     def g(self):
102         "Hour, 12-hour format without leading zeros; i.e. '1' to '12'"
103         if self.data.hour == 0:
104             return 12
105         if self.data.hour > 12:
106             return self.data.hour - 12
107         return self.data.hour
108 
109     def G(self):
110         "Hour, 24-hour format without leading zeros; i.e. '0' to '23'"
111         return self.data.hour
112 
113     def h(self):
114         "Hour, 12-hour format; i.e. '01' to '12'"
115         return '%02d' % self.g()
116 
117     def H(self):
118         "Hour, 24-hour format; i.e. '00' to '23'"
119         return '%02d' % self.G()
120 
121     def i(self):
122         "Minutes; i.e. '00' to '59'"
123         return '%02d' % self.data.minute
124 
125     def O(self):  # NOQA: E743, E741
126         """
127         Difference to Greenwich time in hours; e.g. '+0200', '-0430'.
128 
129         If timezone information is not available, return an empty string.
130         """
131         if not self.timezone:
132             return ""
133 
134         seconds = self.Z()
135         if seconds == "":
136             return ""
137         sign = '-' if seconds < 0 else '+'
138         seconds = abs(seconds)
139         return "%s%02d%02d" % (sign, seconds // 3600, (seconds // 60) % 60)
140 
141     def P(self):
142         """
143         Time, in 12-hour hours, minutes and 'a.m.'/'p.m.', with minutes left off
144         if they're zero and the strings 'midnight' and 'noon' if appropriate.
145         Examples: '1 a.m.', '1:30 p.m.', 'midnight', 'noon', '12:30 p.m.'
146         Proprietary extension.
147         """
148         if self.data.minute == 0 and self.data.hour == 0:
149             return _('midnight')
150         if self.data.minute == 0 and self.data.hour == 12:
151             return _('noon')
152         return '%s %s' % (self.f(), self.a())
153 
154     def s(self):
155         "Seconds; i.e. '00' to '59'"
156         return '%02d' % self.data.second
157 
158     def T(self):
159         """
160         Time zone of this machine; e.g. 'EST' or 'MDT'.
161 
162         If timezone information is not available, return an empty string.
163         """
164         if not self.timezone:
165             return ""
166 
167         name = None
168         try:
169             name = self.timezone.tzname(self.data)
170         except Exception:
171             # pytz raises AmbiguousTimeError during the autumn DST change.
172             # This happens mainly when __init__ receives a naive datetime
173             # and sets self.timezone = get_default_timezone().
174             pass
175         if name is None:
176             name = self.format('O')
177         return str(name)
178 
179     def u(self):
180         "Microseconds; i.e. '000000' to '999999'"
181         return '%06d' % self.data.microsecond
182 
183     def Z(self):
184         """
185         Time zone offset in seconds (i.e. '-43200' to '43200'). The offset for
186         timezones west of UTC is always negative, and for those east of UTC is
187         always positive.
188 
189         If timezone information is not available, return an empty string.
190         """
191         if not self.timezone:
192             return ""
193 
194         try:
195             offset = self.timezone.utcoffset(self.data)
196         except Exception:
197             # pytz raises AmbiguousTimeError during the autumn DST change.
198             # This happens mainly when __init__ receives a naive datetime
199             # and sets self.timezone = get_default_timezone().
200             return ""
201 
202         # `offset` is a datetime.timedelta. For negative values (to the west of
203         # UTC) only days can be negative (days=-1) and seconds are always
204         # positive. e.g. UTC-1 -> timedelta(days=-1, seconds=82800, microseconds=0)
205         # Positive offsets have days=0
206         return offset.days * 86400 + offset.seconds
207 
208 
209 class DateFormat(TimeFormat):
210     def b(self):
211         "Month, textual, 3 letters, lowercase; e.g. 'jan'"
212         return MONTHS_3[self.data.month]
213 
214     def c(self):
215         """
216         ISO 8601 Format
217         Example : '2008-01-02T10:30:00.000123'
218         """
219         return self.data.isoformat()
220 
221     def d(self):
222         "Day of the month, 2 digits with leading zeros; i.e. '01' to '31'"
223         return '%02d' % self.data.day
224 
225     def D(self):
226         "Day of the week, textual, 3 letters; e.g. 'Fri'"
227         return WEEKDAYS_ABBR[self.data.weekday()]
228 
229     def E(self):
230         "Alternative month names as required by some locales. Proprietary extension."
231         return MONTHS_ALT[self.data.month]
232 
233     def F(self):
234         "Month, textual, long; e.g. 'January'"
235         return MONTHS[self.data.month]
236 
237     def I(self):  # NOQA: E743, E741
238         "'1' if Daylight Savings Time, '0' otherwise."
239         try:
240             if self.timezone and self.timezone.dst(self.data):
241                 return '1'
242             else:
243                 return '0'
244         except Exception:
245             # pytz raises AmbiguousTimeError during the autumn DST change.
246             # This happens mainly when __init__ receives a naive datetime
247             # and sets self.timezone = get_default_timezone().
248             return ''
249 
250     def j(self):
251         "Day of the month without leading zeros; i.e. '1' to '31'"
252         return self.data.day
253 
254     def l(self):  # NOQA: E743, E741
255         "Day of the week, textual, long; e.g. 'Friday'"
256         return WEEKDAYS[self.data.weekday()]
257 
258     def L(self):
259         "Boolean for whether it is a leap year; i.e. True or False"
260         return calendar.isleap(self.data.year)
261 
262     def m(self):
263         "Month; i.e. '01' to '12'"
264         return '%02d' % self.data.month
265 
266     def M(self):
267         "Month, textual, 3 letters; e.g. 'Jan'"
268         return MONTHS_3[self.data.month].title()
269 
270     def n(self):
271         "Month without leading zeros; i.e. '1' to '12'"
272         return self.data.month
273 
274     def N(self):
275         "Month abbreviation in Associated Press style. Proprietary extension."
276         return MONTHS_AP[self.data.month]
277 
278     def o(self):
279         "ISO 8601 year number matching the ISO week number (W)"
280         return self.data.isocalendar()[0]
281 
282     def r(self):
283         "RFC 5322 formatted date; e.g. 'Thu, 21 Dec 2000 16:01:07 +0200'"
284         if type(self.data) is datetime.date:
285             raise TypeError(
286                 "The format for date objects may not contain time-related "
287                 "format specifiers (found 'r')."
288             )
289         if is_naive(self.data):
290             dt = make_aware(self.data, timezone=self.timezone)
291         else:
292             dt = self.data
293         return format_datetime_rfc5322(dt)
294 
295     def S(self):
296         "English ordinal suffix for the day of the month, 2 characters; i.e. 'st', 'nd', 'rd' or 'th'"
297         if self.data.day in (11, 12, 13):  # Special case
298             return 'th'
299         last = self.data.day % 10
300         if last == 1:
301             return 'st'
302         if last == 2:
303             return 'nd'
304         if last == 3:
305             return 'rd'
306         return 'th'
307 
308     def t(self):
309         "Number of days in the given month; i.e. '28' to '31'"
310         return '%02d' % calendar.monthrange(self.data.year, self.data.month)[1]
311 
312     def U(self):
313         "Seconds since the Unix epoch (January 1 1970 00:00:00 GMT)"
314         if isinstance(self.data, datetime.datetime) and is_aware(self.data):
315             return int(calendar.timegm(self.data.utctimetuple()))
316         else:
317             return int(time.mktime(self.data.timetuple()))
318 
319     def w(self):
320         "Day of the week, numeric, i.e. '0' (Sunday) to '6' (Saturday)"
321         return (self.data.weekday() + 1) % 7
322 
323     def W(self):
324         "ISO-8601 week number of year, weeks starting on Monday"
325         return self.data.isocalendar()[1]
326 
327     def y(self):
328         "Year, 2 digits; e.g. '99'"
329         return str(self.data.year)[2:]
330 
331     def Y(self):
332         "Year, 4 digits; e.g. '1999'"
333         return self.data.year
334 
335     def z(self):
336         """Day of the year, i.e. 1 to 366."""
337         return self.data.timetuple().tm_yday
338 
339 
340 def format(value, format_string):
341     "Convenience function"
342     df = DateFormat(value)
343     return df.format(format_string)
344 
345 
346 def time_format(value, format_string):
347     "Convenience function"
348     tf = TimeFormat(value)
349     return tf.format(format_string)
350 
[end of django/utils/dateformat.py]
[start of django/utils/dateparse.py]
1 """Functions to parse datetime objects."""
2 
3 # We're using regular expressions rather than time.strptime because:
4 # - They provide both validation and parsing.
5 # - They're more flexible for datetimes.
6 # - The date/datetime/time constructors produce friendlier error messages.
7 
8 import datetime
9 
10 from django.utils.regex_helper import _lazy_re_compile
11 from django.utils.timezone import get_fixed_timezone, utc
12 
13 date_re = _lazy_re_compile(
14     r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})$'
15 )
16 
17 time_re = _lazy_re_compile(
18     r'(?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
19     r'(?::(?P<second>\d{1,2})(?:[\.,](?P<microsecond>\d{1,6})\d{0,6})?)?'
20 )
21 
22 datetime_re = _lazy_re_compile(
23     r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})'
24     r'[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
25     r'(?::(?P<second>\d{1,2})(?:[\.,](?P<microsecond>\d{1,6})\d{0,6})?)?'
26     r'(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?$'
27 )
28 
29 standard_duration_re = _lazy_re_compile(
30     r'^'
31     r'(?:(?P<days>-?\d+) (days?, )?)?'
32     r'(?P<sign>-?)'
33     r'((?:(?P<hours>\d+):)(?=\d+:\d+))?'
34     r'(?:(?P<minutes>\d+):)?'
35     r'(?P<seconds>\d+)'
36     r'(?:[\.,](?P<microseconds>\d{1,6})\d{0,6})?'
37     r'$'
38 )
39 
40 # Support the sections of ISO 8601 date representation that are accepted by
41 # timedelta
42 iso8601_duration_re = _lazy_re_compile(
43     r'^(?P<sign>[-+]?)'
44     r'P'
45     r'(?:(?P<days>\d+(.\d+)?)D)?'
46     r'(?:T'
47     r'(?:(?P<hours>\d+(.\d+)?)H)?'
48     r'(?:(?P<minutes>\d+(.\d+)?)M)?'
49     r'(?:(?P<seconds>\d+(.\d+)?)S)?'
50     r')?'
51     r'$'
52 )
53 
54 # Support PostgreSQL's day-time interval format, e.g. "3 days 04:05:06". The
55 # year-month and mixed intervals cannot be converted to a timedelta and thus
56 # aren't accepted.
57 postgres_interval_re = _lazy_re_compile(
58     r'^'
59     r'(?:(?P<days>-?\d+) (days? ?))?'
60     r'(?:(?P<sign>[-+])?'
61     r'(?P<hours>\d+):'
62     r'(?P<minutes>\d\d):'
63     r'(?P<seconds>\d\d)'
64     r'(?:\.(?P<microseconds>\d{1,6}))?'
65     r')?$'
66 )
67 
68 
69 def parse_date(value):
70     """Parse a string and return a datetime.date.
71 
72     Raise ValueError if the input is well formatted but not a valid date.
73     Return None if the input isn't well formatted.
74     """
75     match = date_re.match(value)
76     if match:
77         kw = {k: int(v) for k, v in match.groupdict().items()}
78         return datetime.date(**kw)
79 
80 
81 def parse_time(value):
82     """Parse a string and return a datetime.time.
83 
84     This function doesn't support time zone offsets.
85 
86     Raise ValueError if the input is well formatted but not a valid time.
87     Return None if the input isn't well formatted, in particular if it
88     contains an offset.
89     """
90     match = time_re.match(value)
91     if match:
92         kw = match.groupdict()
93         kw['microsecond'] = kw['microsecond'] and kw['microsecond'].ljust(6, '0')
94         kw = {k: int(v) for k, v in kw.items() if v is not None}
95         return datetime.time(**kw)
96 
97 
98 def parse_datetime(value):
99     """Parse a string and return a datetime.datetime.
100 
101     This function supports time zone offsets. When the input contains one,
102     the output uses a timezone with a fixed offset from UTC.
103 
104     Raise ValueError if the input is well formatted but not a valid datetime.
105     Return None if the input isn't well formatted.
106     """
107     match = datetime_re.match(value)
108     if match:
109         kw = match.groupdict()
110         kw['microsecond'] = kw['microsecond'] and kw['microsecond'].ljust(6, '0')
111         tzinfo = kw.pop('tzinfo')
112         if tzinfo == 'Z':
113             tzinfo = utc
114         elif tzinfo is not None:
115             offset_mins = int(tzinfo[-2:]) if len(tzinfo) > 3 else 0
116             offset = 60 * int(tzinfo[1:3]) + offset_mins
117             if tzinfo[0] == '-':
118                 offset = -offset
119             tzinfo = get_fixed_timezone(offset)
120         kw = {k: int(v) for k, v in kw.items() if v is not None}
121         kw['tzinfo'] = tzinfo
122         return datetime.datetime(**kw)
123 
124 
125 def parse_duration(value):
126     """Parse a duration string and return a datetime.timedelta.
127 
128     The preferred format for durations in Django is '%d %H:%M:%S.%f'.
129 
130     Also supports ISO 8601 representation and PostgreSQL's day-time interval
131     format.
132     """
133     match = (
134         standard_duration_re.match(value) or
135         iso8601_duration_re.match(value) or
136         postgres_interval_re.match(value)
137     )
138     if match:
139         kw = match.groupdict()
140         sign = -1 if kw.pop('sign', '+') == '-' else 1
141         if kw.get('microseconds'):
142             kw['microseconds'] = kw['microseconds'].ljust(6, '0')
143         if kw.get('seconds') and kw.get('microseconds') and kw['seconds'].startswith('-'):
144             kw['microseconds'] = '-' + kw['microseconds']
145         kw = {k: float(v.replace(',', '.')) for k, v in kw.items() if v is not None}
146         days = datetime.timedelta(kw.pop('days', .0) or .0)
147         return days + sign * datetime.timedelta(**kw)
148 
[end of django/utils/dateparse.py]
[start of django/views/generic/dates.py]
1 import datetime
2 
3 from django.conf import settings
4 from django.core.exceptions import ImproperlyConfigured
5 from django.db import models
6 from django.http import Http404
7 from django.utils import timezone
8 from django.utils.functional import cached_property
9 from django.utils.translation import gettext as _
10 from django.views.generic.base import View
11 from django.views.generic.detail import (
12     BaseDetailView, SingleObjectTemplateResponseMixin,
13 )
14 from django.views.generic.list import (
15     MultipleObjectMixin, MultipleObjectTemplateResponseMixin,
16 )
17 
18 
19 class YearMixin:
20     """Mixin for views manipulating year-based data."""
21     year_format = '%Y'
22     year = None
23 
24     def get_year_format(self):
25         """
26         Get a year format string in strptime syntax to be used to parse the
27         year from url variables.
28         """
29         return self.year_format
30 
31     def get_year(self):
32         """Return the year for which this view should display data."""
33         year = self.year
34         if year is None:
35             try:
36                 year = self.kwargs['year']
37             except KeyError:
38                 try:
39                     year = self.request.GET['year']
40                 except KeyError:
41                     raise Http404(_("No year specified"))
42         return year
43 
44     def get_next_year(self, date):
45         """Get the next valid year."""
46         return _get_next_prev(self, date, is_previous=False, period='year')
47 
48     def get_previous_year(self, date):
49         """Get the previous valid year."""
50         return _get_next_prev(self, date, is_previous=True, period='year')
51 
52     def _get_next_year(self, date):
53         """
54         Return the start date of the next interval.
55 
56         The interval is defined by start date <= item date < next start date.
57         """
58         try:
59             return date.replace(year=date.year + 1, month=1, day=1)
60         except ValueError:
61             raise Http404(_("Date out of range"))
62 
63     def _get_current_year(self, date):
64         """Return the start date of the current interval."""
65         return date.replace(month=1, day=1)
66 
67 
68 class MonthMixin:
69     """Mixin for views manipulating month-based data."""
70     month_format = '%b'
71     month = None
72 
73     def get_month_format(self):
74         """
75         Get a month format string in strptime syntax to be used to parse the
76         month from url variables.
77         """
78         return self.month_format
79 
80     def get_month(self):
81         """Return the month for which this view should display data."""
82         month = self.month
83         if month is None:
84             try:
85                 month = self.kwargs['month']
86             except KeyError:
87                 try:
88                     month = self.request.GET['month']
89                 except KeyError:
90                     raise Http404(_("No month specified"))
91         return month
92 
93     def get_next_month(self, date):
94         """Get the next valid month."""
95         return _get_next_prev(self, date, is_previous=False, period='month')
96 
97     def get_previous_month(self, date):
98         """Get the previous valid month."""
99         return _get_next_prev(self, date, is_previous=True, period='month')
100 
101     def _get_next_month(self, date):
102         """
103         Return the start date of the next interval.
104 
105         The interval is defined by start date <= item date < next start date.
106         """
107         if date.month == 12:
108             try:
109                 return date.replace(year=date.year + 1, month=1, day=1)
110             except ValueError:
111                 raise Http404(_("Date out of range"))
112         else:
113             return date.replace(month=date.month + 1, day=1)
114 
115     def _get_current_month(self, date):
116         """Return the start date of the previous interval."""
117         return date.replace(day=1)
118 
119 
120 class DayMixin:
121     """Mixin for views manipulating day-based data."""
122     day_format = '%d'
123     day = None
124 
125     def get_day_format(self):
126         """
127         Get a day format string in strptime syntax to be used to parse the day
128         from url variables.
129         """
130         return self.day_format
131 
132     def get_day(self):
133         """Return the day for which this view should display data."""
134         day = self.day
135         if day is None:
136             try:
137                 day = self.kwargs['day']
138             except KeyError:
139                 try:
140                     day = self.request.GET['day']
141                 except KeyError:
142                     raise Http404(_("No day specified"))
143         return day
144 
145     def get_next_day(self, date):
146         """Get the next valid day."""
147         return _get_next_prev(self, date, is_previous=False, period='day')
148 
149     def get_previous_day(self, date):
150         """Get the previous valid day."""
151         return _get_next_prev(self, date, is_previous=True, period='day')
152 
153     def _get_next_day(self, date):
154         """
155         Return the start date of the next interval.
156 
157         The interval is defined by start date <= item date < next start date.
158         """
159         return date + datetime.timedelta(days=1)
160 
161     def _get_current_day(self, date):
162         """Return the start date of the current interval."""
163         return date
164 
165 
166 class WeekMixin:
167     """Mixin for views manipulating week-based data."""
168     week_format = '%U'
169     week = None
170 
171     def get_week_format(self):
172         """
173         Get a week format string in strptime syntax to be used to parse the
174         week from url variables.
175         """
176         return self.week_format
177 
178     def get_week(self):
179         """Return the week for which this view should display data."""
180         week = self.week
181         if week is None:
182             try:
183                 week = self.kwargs['week']
184             except KeyError:
185                 try:
186                     week = self.request.GET['week']
187                 except KeyError:
188                     raise Http404(_("No week specified"))
189         return week
190 
191     def get_next_week(self, date):
192         """Get the next valid week."""
193         return _get_next_prev(self, date, is_previous=False, period='week')
194 
195     def get_previous_week(self, date):
196         """Get the previous valid week."""
197         return _get_next_prev(self, date, is_previous=True, period='week')
198 
199     def _get_next_week(self, date):
200         """
201         Return the start date of the next interval.
202 
203         The interval is defined by start date <= item date < next start date.
204         """
205         try:
206             return date + datetime.timedelta(days=7 - self._get_weekday(date))
207         except OverflowError:
208             raise Http404(_("Date out of range"))
209 
210     def _get_current_week(self, date):
211         """Return the start date of the current interval."""
212         return date - datetime.timedelta(self._get_weekday(date))
213 
214     def _get_weekday(self, date):
215         """
216         Return the weekday for a given date.
217 
218         The first day according to the week format is 0 and the last day is 6.
219         """
220         week_format = self.get_week_format()
221         if week_format == '%W':                 # week starts on Monday
222             return date.weekday()
223         elif week_format == '%U':               # week starts on Sunday
224             return (date.weekday() + 1) % 7
225         else:
226             raise ValueError("unknown week format: %s" % week_format)
227 
228 
229 class DateMixin:
230     """Mixin class for views manipulating date-based data."""
231     date_field = None
232     allow_future = False
233 
234     def get_date_field(self):
235         """Get the name of the date field to be used to filter by."""
236         if self.date_field is None:
237             raise ImproperlyConfigured("%s.date_field is required." % self.__class__.__name__)
238         return self.date_field
239 
240     def get_allow_future(self):
241         """
242         Return `True` if the view should be allowed to display objects from
243         the future.
244         """
245         return self.allow_future
246 
247     # Note: the following three methods only work in subclasses that also
248     # inherit SingleObjectMixin or MultipleObjectMixin.
249 
250     @cached_property
251     def uses_datetime_field(self):
252         """
253         Return `True` if the date field is a `DateTimeField` and `False`
254         if it's a `DateField`.
255         """
256         model = self.get_queryset().model if self.model is None else self.model
257         field = model._meta.get_field(self.get_date_field())
258         return isinstance(field, models.DateTimeField)
259 
260     def _make_date_lookup_arg(self, value):
261         """
262         Convert a date into a datetime when the date field is a DateTimeField.
263 
264         When time zone support is enabled, `date` is assumed to be in the
265         current time zone, so that displayed items are consistent with the URL.
266         """
267         if self.uses_datetime_field:
268             value = datetime.datetime.combine(value, datetime.time.min)
269             if settings.USE_TZ:
270                 value = timezone.make_aware(value)
271         return value
272 
273     def _make_single_date_lookup(self, date):
274         """
275         Get the lookup kwargs for filtering on a single date.
276 
277         If the date field is a DateTimeField, we can't just filter on
278         date_field=date because that doesn't take the time into account.
279         """
280         date_field = self.get_date_field()
281         if self.uses_datetime_field:
282             since = self._make_date_lookup_arg(date)
283             until = self._make_date_lookup_arg(date + datetime.timedelta(days=1))
284             return {
285                 '%s__gte' % date_field: since,
286                 '%s__lt' % date_field: until,
287             }
288         else:
289             # Skip self._make_date_lookup_arg, it's a no-op in this branch.
290             return {date_field: date}
291 
292 
293 class BaseDateListView(MultipleObjectMixin, DateMixin, View):
294     """Abstract base class for date-based views displaying a list of objects."""
295     allow_empty = False
296     date_list_period = 'year'
297 
298     def get(self, request, *args, **kwargs):
299         self.date_list, self.object_list, extra_context = self.get_dated_items()
300         context = self.get_context_data(
301             object_list=self.object_list,
302             date_list=self.date_list,
303             **extra_context
304         )
305         return self.render_to_response(context)
306 
307     def get_dated_items(self):
308         """Obtain the list of dates and items."""
309         raise NotImplementedError('A DateView must provide an implementation of get_dated_items()')
310 
311     def get_ordering(self):
312         """
313         Return the field or fields to use for ordering the queryset; use the
314         date field by default.
315         """
316         return '-%s' % self.get_date_field() if self.ordering is None else self.ordering
317 
318     def get_dated_queryset(self, **lookup):
319         """
320         Get a queryset properly filtered according to `allow_future` and any
321         extra lookup kwargs.
322         """
323         qs = self.get_queryset().filter(**lookup)
324         date_field = self.get_date_field()
325         allow_future = self.get_allow_future()
326         allow_empty = self.get_allow_empty()
327         paginate_by = self.get_paginate_by(qs)
328 
329         if not allow_future:
330             now = timezone.now() if self.uses_datetime_field else timezone_today()
331             qs = qs.filter(**{'%s__lte' % date_field: now})
332 
333         if not allow_empty:
334             # When pagination is enabled, it's better to do a cheap query
335             # than to load the unpaginated queryset in memory.
336             is_empty = not qs if paginate_by is None else not qs.exists()
337             if is_empty:
338                 raise Http404(_("No %(verbose_name_plural)s available") % {
339                     'verbose_name_plural': qs.model._meta.verbose_name_plural,
340                 })
341 
342         return qs
343 
344     def get_date_list_period(self):
345         """
346         Get the aggregation period for the list of dates: 'year', 'month', or
347         'day'.
348         """
349         return self.date_list_period
350 
351     def get_date_list(self, queryset, date_type=None, ordering='ASC'):
352         """
353         Get a date list by calling `queryset.dates/datetimes()`, checking
354         along the way for empty lists that aren't allowed.
355         """
356         date_field = self.get_date_field()
357         allow_empty = self.get_allow_empty()
358         if date_type is None:
359             date_type = self.get_date_list_period()
360 
361         if self.uses_datetime_field:
362             date_list = queryset.datetimes(date_field, date_type, ordering)
363         else:
364             date_list = queryset.dates(date_field, date_type, ordering)
365         if date_list is not None and not date_list and not allow_empty:
366             raise Http404(
367                 _("No %(verbose_name_plural)s available") % {
368                     'verbose_name_plural': queryset.model._meta.verbose_name_plural,
369                 }
370             )
371 
372         return date_list
373 
374 
375 class BaseArchiveIndexView(BaseDateListView):
376     """
377     Base class for archives of date-based items. Requires a response mixin.
378     """
379     context_object_name = 'latest'
380 
381     def get_dated_items(self):
382         """Return (date_list, items, extra_context) for this request."""
383         qs = self.get_dated_queryset()
384         date_list = self.get_date_list(qs, ordering='DESC')
385 
386         if not date_list:
387             qs = qs.none()
388 
389         return (date_list, qs, {})
390 
391 
392 class ArchiveIndexView(MultipleObjectTemplateResponseMixin, BaseArchiveIndexView):
393     """Top-level archive of date-based items."""
394     template_name_suffix = '_archive'
395 
396 
397 class BaseYearArchiveView(YearMixin, BaseDateListView):
398     """List of objects published in a given year."""
399     date_list_period = 'month'
400     make_object_list = False
401 
402     def get_dated_items(self):
403         """Return (date_list, items, extra_context) for this request."""
404         year = self.get_year()
405 
406         date_field = self.get_date_field()
407         date = _date_from_string(year, self.get_year_format())
408 
409         since = self._make_date_lookup_arg(date)
410         until = self._make_date_lookup_arg(self._get_next_year(date))
411         lookup_kwargs = {
412             '%s__gte' % date_field: since,
413             '%s__lt' % date_field: until,
414         }
415 
416         qs = self.get_dated_queryset(**lookup_kwargs)
417         date_list = self.get_date_list(qs)
418 
419         if not self.get_make_object_list():
420             # We need this to be a queryset since parent classes introspect it
421             # to find information about the model.
422             qs = qs.none()
423 
424         return (date_list, qs, {
425             'year': date,
426             'next_year': self.get_next_year(date),
427             'previous_year': self.get_previous_year(date),
428         })
429 
430     def get_make_object_list(self):
431         """
432         Return `True` if this view should contain the full list of objects in
433         the given year.
434         """
435         return self.make_object_list
436 
437 
438 class YearArchiveView(MultipleObjectTemplateResponseMixin, BaseYearArchiveView):
439     """List of objects published in a given year."""
440     template_name_suffix = '_archive_year'
441 
442 
443 class BaseMonthArchiveView(YearMixin, MonthMixin, BaseDateListView):
444     """List of objects published in a given month."""
445     date_list_period = 'day'
446 
447     def get_dated_items(self):
448         """Return (date_list, items, extra_context) for this request."""
449         year = self.get_year()
450         month = self.get_month()
451 
452         date_field = self.get_date_field()
453         date = _date_from_string(year, self.get_year_format(),
454                                  month, self.get_month_format())
455 
456         since = self._make_date_lookup_arg(date)
457         until = self._make_date_lookup_arg(self._get_next_month(date))
458         lookup_kwargs = {
459             '%s__gte' % date_field: since,
460             '%s__lt' % date_field: until,
461         }
462 
463         qs = self.get_dated_queryset(**lookup_kwargs)
464         date_list = self.get_date_list(qs)
465 
466         return (date_list, qs, {
467             'month': date,
468             'next_month': self.get_next_month(date),
469             'previous_month': self.get_previous_month(date),
470         })
471 
472 
473 class MonthArchiveView(MultipleObjectTemplateResponseMixin, BaseMonthArchiveView):
474     """List of objects published in a given month."""
475     template_name_suffix = '_archive_month'
476 
477 
478 class BaseWeekArchiveView(YearMixin, WeekMixin, BaseDateListView):
479     """List of objects published in a given week."""
480 
481     def get_dated_items(self):
482         """Return (date_list, items, extra_context) for this request."""
483         year = self.get_year()
484         week = self.get_week()
485 
486         date_field = self.get_date_field()
487         week_format = self.get_week_format()
488         week_choices = {'%W': '1', '%U': '0'}
489         try:
490             week_start = week_choices[week_format]
491         except KeyError:
492             raise ValueError('Unknown week format %r. Choices are: %s' % (
493                 week_format,
494                 ', '.join(sorted(week_choices)),
495             ))
496         date = _date_from_string(year, self.get_year_format(),
497                                  week_start, '%w',
498                                  week, week_format)
499 
500         since = self._make_date_lookup_arg(date)
501         until = self._make_date_lookup_arg(self._get_next_week(date))
502         lookup_kwargs = {
503             '%s__gte' % date_field: since,
504             '%s__lt' % date_field: until,
505         }
506 
507         qs = self.get_dated_queryset(**lookup_kwargs)
508 
509         return (None, qs, {
510             'week': date,
511             'next_week': self.get_next_week(date),
512             'previous_week': self.get_previous_week(date),
513         })
514 
515 
516 class WeekArchiveView(MultipleObjectTemplateResponseMixin, BaseWeekArchiveView):
517     """List of objects published in a given week."""
518     template_name_suffix = '_archive_week'
519 
520 
521 class BaseDayArchiveView(YearMixin, MonthMixin, DayMixin, BaseDateListView):
522     """List of objects published on a given day."""
523     def get_dated_items(self):
524         """Return (date_list, items, extra_context) for this request."""
525         year = self.get_year()
526         month = self.get_month()
527         day = self.get_day()
528 
529         date = _date_from_string(year, self.get_year_format(),
530                                  month, self.get_month_format(),
531                                  day, self.get_day_format())
532 
533         return self._get_dated_items(date)
534 
535     def _get_dated_items(self, date):
536         """
537         Do the actual heavy lifting of getting the dated items; this accepts a
538         date object so that TodayArchiveView can be trivial.
539         """
540         lookup_kwargs = self._make_single_date_lookup(date)
541         qs = self.get_dated_queryset(**lookup_kwargs)
542 
543         return (None, qs, {
544             'day': date,
545             'previous_day': self.get_previous_day(date),
546             'next_day': self.get_next_day(date),
547             'previous_month': self.get_previous_month(date),
548             'next_month': self.get_next_month(date)
549         })
550 
551 
552 class DayArchiveView(MultipleObjectTemplateResponseMixin, BaseDayArchiveView):
553     """List of objects published on a given day."""
554     template_name_suffix = "_archive_day"
555 
556 
557 class BaseTodayArchiveView(BaseDayArchiveView):
558     """List of objects published today."""
559 
560     def get_dated_items(self):
561         """Return (date_list, items, extra_context) for this request."""
562         return self._get_dated_items(datetime.date.today())
563 
564 
565 class TodayArchiveView(MultipleObjectTemplateResponseMixin, BaseTodayArchiveView):
566     """List of objects published today."""
567     template_name_suffix = "_archive_day"
568 
569 
570 class BaseDateDetailView(YearMixin, MonthMixin, DayMixin, DateMixin, BaseDetailView):
571     """
572     Detail view of a single object on a single date; this differs from the
573     standard DetailView by accepting a year/month/day in the URL.
574     """
575     def get_object(self, queryset=None):
576         """Get the object this request displays."""
577         year = self.get_year()
578         month = self.get_month()
579         day = self.get_day()
580         date = _date_from_string(year, self.get_year_format(),
581                                  month, self.get_month_format(),
582                                  day, self.get_day_format())
583 
584         # Use a custom queryset if provided
585         qs = self.get_queryset() if queryset is None else queryset
586 
587         if not self.get_allow_future() and date > datetime.date.today():
588             raise Http404(_(
589                 "Future %(verbose_name_plural)s not available because "
590                 "%(class_name)s.allow_future is False."
591             ) % {
592                 'verbose_name_plural': qs.model._meta.verbose_name_plural,
593                 'class_name': self.__class__.__name__,
594             })
595 
596         # Filter down a queryset from self.queryset using the date from the
597         # URL. This'll get passed as the queryset to DetailView.get_object,
598         # which'll handle the 404
599         lookup_kwargs = self._make_single_date_lookup(date)
600         qs = qs.filter(**lookup_kwargs)
601 
602         return super().get_object(queryset=qs)
603 
604 
605 class DateDetailView(SingleObjectTemplateResponseMixin, BaseDateDetailView):
606     """
607     Detail view of a single object on a single date; this differs from the
608     standard DetailView by accepting a year/month/day in the URL.
609     """
610     template_name_suffix = '_detail'
611 
612 
613 def _date_from_string(year, year_format, month='', month_format='', day='', day_format='', delim='__'):
614     """
615     Get a datetime.date object given a format string and a year, month, and day
616     (only year is mandatory). Raise a 404 for an invalid date.
617     """
618     format = year_format + delim + month_format + delim + day_format
619     datestr = str(year) + delim + str(month) + delim + str(day)
620     try:
621         return datetime.datetime.strptime(datestr, format).date()
622     except ValueError:
623         raise Http404(_('Invalid date string “%(datestr)s” given format “%(format)s”') % {
624             'datestr': datestr,
625             'format': format,
626         })
627 
628 
629 def _get_next_prev(generic_view, date, is_previous, period):
630     """
631     Get the next or the previous valid date. The idea is to allow links on
632     month/day views to never be 404s by never providing a date that'll be
633     invalid for the given view.
634 
635     This is a bit complicated since it handles different intervals of time,
636     hence the coupling to generic_view.
637 
638     However in essence the logic comes down to:
639 
640         * If allow_empty and allow_future are both true, this is easy: just
641           return the naive result (just the next/previous day/week/month,
642           regardless of object existence.)
643 
644         * If allow_empty is true, allow_future is false, and the naive result
645           isn't in the future, then return it; otherwise return None.
646 
647         * If allow_empty is false and allow_future is true, return the next
648           date *that contains a valid object*, even if it's in the future. If
649           there are no next objects, return None.
650 
651         * If allow_empty is false and allow_future is false, return the next
652           date that contains a valid object. If that date is in the future, or
653           if there are no next objects, return None.
654     """
655     date_field = generic_view.get_date_field()
656     allow_empty = generic_view.get_allow_empty()
657     allow_future = generic_view.get_allow_future()
658 
659     get_current = getattr(generic_view, '_get_current_%s' % period)
660     get_next = getattr(generic_view, '_get_next_%s' % period)
661 
662     # Bounds of the current interval
663     start, end = get_current(date), get_next(date)
664 
665     # If allow_empty is True, the naive result will be valid
666     if allow_empty:
667         if is_previous:
668             result = get_current(start - datetime.timedelta(days=1))
669         else:
670             result = end
671 
672         if allow_future or result <= timezone_today():
673             return result
674         else:
675             return None
676 
677     # Otherwise, we'll need to go to the database to look for an object
678     # whose date_field is at least (greater than/less than) the given
679     # naive result
680     else:
681         # Construct a lookup and an ordering depending on whether we're doing
682         # a previous date or a next date lookup.
683         if is_previous:
684             lookup = {'%s__lt' % date_field: generic_view._make_date_lookup_arg(start)}
685             ordering = '-%s' % date_field
686         else:
687             lookup = {'%s__gte' % date_field: generic_view._make_date_lookup_arg(end)}
688             ordering = date_field
689 
690         # Filter out objects in the future if appropriate.
691         if not allow_future:
692             # Fortunately, to match the implementation of allow_future,
693             # we need __lte, which doesn't conflict with __lt above.
694             if generic_view.uses_datetime_field:
695                 now = timezone.now()
696             else:
697                 now = timezone_today()
698             lookup['%s__lte' % date_field] = now
699 
700         qs = generic_view.get_queryset().filter(**lookup).order_by(ordering)
701 
702         # Snag the first object from the queryset; if it doesn't exist that
703         # means there's no next/previous link available.
704         try:
705             result = getattr(qs[0], date_field)
706         except IndexError:
707             return None
708 
709         # Convert datetimes to dates in the current time zone.
710         if generic_view.uses_datetime_field:
711             if settings.USE_TZ:
712                 result = timezone.localtime(result)
713             result = result.date()
714 
715         # Return the first day of the period.
716         return get_current(result)
717 
718 
719 def timezone_today():
720     """Return the current date in the current time zone."""
721     if settings.USE_TZ:
722         return timezone.localdate()
723     else:
724         return datetime.date.today()
725 
[end of django/views/generic/dates.py]
</code>
I need you to solve this issue by generating a single patch file that I can apply directly to this repository using git apply. Please respond with a single patch file in the following format.
<patch>
--- a/file.py
+++ b/file.py
@@ -1,27 +1,35 @@
 def euclidean(a, b):
-    while b:
-        a, b = b, a % b
-    return a
+    if b == 0:
+        return a
+    return euclidean(b, a % b)
 
 
 def bresenham(x0, y0, x1, y1):
     points = []
     dx = abs(x1 - x0)
     dy = abs(y1 - y0)
-    sx = 1 if x0 < x1 else -1
-    sy = 1 if y0 < y1 else -1
-    err = dx - dy
+    x, y = x0, y0
+    sx = -1 if x0 > x1 else 1
+    sy = -1 if y0 > y1 else 1
 
-    while True:
-        points.append((x0, y0))
-        if x0 == x1 and y0 == y1:
-            break
-        e2 = 2 * err
-        if e2 > -dy:
+    if dx > dy:
+        err = dx / 2.0
+        while x != x1:
+            points.append((x, y))
             err -= dy
-            x0 += sx
-        if e2 < dx:
-            err += dx
-            y0 += sy
+            if err < 0:
+                y += sy
+                err += dx
+            x += sx
+    else:
+        err = dy / 2.0
+        while y != y1:
+            points.append((x, y))
+            err -= dx
+            if err < 0:
+                x += sx
+                err += dy
+            y += sy
 
+    points.append((x, y))
     return points
</patch>

```

