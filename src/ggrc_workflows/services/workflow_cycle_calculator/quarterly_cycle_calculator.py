# Copyright (C) 2015 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: urban@reciprocitylabs.com
# Maintained By: urban@reciprocitylabs.com

import datetime
from dateutil import relativedelta

from cycle_calculator import CycleCalculator

class QuarterlyCycleCalculator(CycleCalculator):
  """CycleCalculator implementation for quarterly workflows.

  Quarterly workflows have a specific date domain that also requires a bit more
  math. Option 1 is for Jan/Apr/Jul/Oct, option 2 is for Feb/May/Aug/Nov and
  option 3 is for Mar/Jun/Sep/Dec. Each task can go UP TO three
  months (non-inclusive).
  """
  time_delta = relativedelta.relativedelta(months=3)

  date_domain = {
    1: {1, 4, 7, 10}, # Jan/Apr/Jul/Oct
    2: {2, 5, 8, 11}, # Feb/May/Aug/Nov
    3: {3, 6, 9, 12}  # Mar/Jun/Sep/Dec
  }

  def __init__(self, workflow, base_date=None):
    super(QuarterlyCycleCalculator, self).__init__(workflow)

    base_date = self.get_base_date(base_date)
    self.reified_tasks = {}
    for task in self.tasks:
      start_date, end_date = self.non_adjusted_task_date_range(task, base_date)
      self.reified_tasks[task.id] = {
        'start_date': start_date,
        'end_date': end_date,
        'relative_start': (task.relative_start_month, task.relative_start_day),
        'relative_end': (task.relative_start_month, task.relative_end_day)
      }

  def relative_day_to_date(self, relative_day, relative_month=None,
                           base_date=None):
    """Converts a quarterly representation of a day into concrete date object.

    Relative month is not the best description, but we have to standardize on
    something (better would be relative_quarter) to ensure consistent calls
    from CycleCalculator.

    First we ensure that we have both relative_day and relative_month or,
    alternatively, that relative_day carries month information as well.

    While task_date_range calls with explicit relative_month, reified_tasks
    stores relative days as MM/DD and we must first convert these values so
    that it can sort and get min and max values for tasks.

    Afterwards we must the LARGEST month for a specified quarter option that
    is SMALLER than base_date's month.

    Afterwards we repeat the math similar to monthly cycle calculator and
    ensure that the day is not overflowing to the next month.
    """
    relative_day = int(relative_day)
    relative_month = int(relative_month)

    base_date = self.get_base_date(base_date)

    # relative_month is 1, 2 or 3 and represents quarterly option, based
    # on which we select the month domain. Month is then the LARGEST
    # number from all the months that were before base_date.month - except
    # at the end of the year when quarter can overflow to next year. In such
    # case it is the MINIMUM.
    month_domain = self.date_domain[relative_month]
    domain = filter(lambda x: x <= base_date.month, month_domain)
    if len(domain):
      month = max(filter(lambda x: x <= base_date.month, month_domain))
    else:
      month = min(month_domain)

    start_month = datetime.date(base_date.year, month, 1)
    ddate = start_month + relativedelta.relativedelta(days=relative_day - 1)

    # We want to go up to the end of the month and not over
    if ddate.month != start_month.month:
      ddate = ddate - relativedelta.relativedelta(days=ddate.day)
    return ddate