"""Print summary statistics."""
import numpy as np
from sklearn.metrics import r2_score, mean_squared_error


def eval_predictions(X_test, y_test, y_pred):
    """Print out some statistics."""
    def summarize(header, y_t, y_p):
        print('-'*66)
        print(header)
        print('-'*66)
        for crime_type in crime_types:
            r2 = r2_score(y_t[crime_type], y_p[crime_type])
            rmse = np.sqrt(
                mean_squared_error(y_t[crime_type], y_p[crime_type])
            )
            underlying_mean = np.mean(y_t[crime_type])

            print(('{0: <17} ' +
                   'R2 = {1:8.1f}, ' +
                   'RMSE = {2:9.3f}, ' +
                   'RMSE (%) = {3:9.3f}').format(
                    crime_type + ':',
                    100*r2,
                    rmse,
                    100*rmse/underlying_mean
            ))
        print()

    crime_types = y_test.select_dtypes(exclude=['object']).columns
    summarize('Four-hour buckets:', y_test, y_pred)

    y_test_with_dates = y_test.merge(
        X_test[[
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH',
            'COMPLAINT_DAY', 'ADDR_PCT_CD'
        ]], left_index=True, right_index=True
    )

    y_test_daily = y_test_with_dates.groupby([
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'COMPLAINT_DAY', 'ADDR_PCT_CD'
    ])[crime_types].sum()
    y_pred_daily = y_pred.groupby([
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'COMPLAINT_DAY', 'ADDR_PCT_CD'
    ])[crime_types].sum()
    summarize('Days:', y_test_daily, y_pred_daily)

    y_test_monthly = y_test_with_dates.groupby([
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'ADDR_PCT_CD'
    ])[crime_types].sum()
    y_pred_monthly = y_pred.groupby([
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'ADDR_PCT_CD'
    ])[crime_types].sum()
    summarize('Months:', y_test_monthly, y_pred_monthly)

    y_test_daily = y_test_with_dates.groupby([
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'COMPLAINT_DAY'
    ])[crime_types].sum()
    y_pred_daily = y_pred.groupby([
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'COMPLAINT_DAY'
    ])[crime_types].sum()
    summarize('Days (All Precincts):', y_test_daily, y_pred_daily)

    y_test_monthly = y_test_with_dates.groupby([
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH'
    ])[crime_types].sum()
    y_pred_monthly = y_pred.groupby([
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH'
    ])[crime_types].sum()
    summarize('Months (All Precincts):', y_test_monthly, y_pred_monthly)
