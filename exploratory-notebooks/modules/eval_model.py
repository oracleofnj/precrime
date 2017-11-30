"""Print summary statistics."""
from sklearn.metrics import r2_score, mean_squared_error


def eval_predictions(X_test, y_test, y_pred):
    """Print out some statistics."""
    crime_types = y_test.select_dtypes(exclude=['object']).columns
    print('-'*40)
    print('Four-hour buckets:')
    print('-'*40)
    for crime_type in crime_types:
        print('{0}: R2 = {1:.1f}, MSE = {2:.4f}'.format(
                crime_type,
                100*r2_score(y_test[crime_type], y_pred[crime_type]),
                mean_squared_error(y_test[crime_type], y_pred[crime_type])
        ))
    print()

    y_test_with_dates = y_test.merge(
        X_test[[
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH',
            'COMPLAINT_DAY', 'ADDR_PCT_CD'
        ]], left_index=True, right_index=True
    )

    print('-'*40)
    print('Days:')
    print('-'*40)
    y_test_daily = y_test_with_dates.groupby([
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'COMPLAINT_DAY', 'ADDR_PCT_CD'
    ])[crime_types].sum()
    y_pred_daily = y_pred.groupby([
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'COMPLAINT_DAY', 'ADDR_PCT_CD'
    ])[crime_types].sum()
    for crime_type in crime_types:
        print('{0}: R2 = {1:.1f}, MSE = {2:.4f}'.format(
                crime_type,
                100*r2_score(
                    y_test_daily[crime_type],
                    y_pred_daily[crime_type]
                ),
                mean_squared_error(
                    y_test_daily[crime_type],
                    y_pred_daily[crime_type]
                )
        ))
    print()

    print('-'*40)
    print('Months:')
    print('-'*40)
    y_test_monthly = y_test_with_dates.groupby([
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'ADDR_PCT_CD'
    ])[crime_types].sum()
    y_pred_monthly = y_pred.groupby([
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'ADDR_PCT_CD'
    ])[crime_types].sum()
    for crime_type in crime_types:
        print('{0}: R2 = {1:.1f}, MSE = {2:.4f}'.format(
                crime_type,
                100*r2_score(
                    y_test_monthly[crime_type],
                    y_pred_monthly[crime_type]
                ),
                mean_squared_error(
                    y_test_monthly[crime_type],
                    y_pred_monthly[crime_type]
                )
        ))
    print()

    print('-'*40)
    print('Days (All Precincts):')
    print('-'*40)
    y_test_daily = y_test_with_dates.groupby([
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'COMPLAINT_DAY'
    ])[crime_types].sum()
    y_pred_daily = y_pred.groupby([
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'COMPLAINT_DAY'
    ])[crime_types].sum()
    for crime_type in crime_types:
        print('{0}: R2 = {1:.1f}, MSE = {2:.4f}'.format(
                crime_type,
                100*r2_score(
                    y_test_daily[crime_type],
                    y_pred_daily[crime_type]
                ),
                mean_squared_error(
                    y_test_daily[crime_type],
                    y_pred_daily[crime_type]
                )
        ))
    print()

    print('-'*40)
    print('Months (All Precincts):')
    print('-'*40)
    y_test_monthly = y_test_with_dates.groupby([
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH'
    ])[crime_types].sum()
    y_pred_monthly = y_pred.groupby([
            'COMPLAINT_YEAR', 'COMPLAINT_MONTH'
    ])[crime_types].sum()
    for crime_type in crime_types:
        print('{0}: R2 = {1:.1f}, MSE = {2:.4f}'.format(
                crime_type,
                100*r2_score(
                    y_test_monthly[crime_type],
                    y_pred_monthly[crime_type]
                ),
                mean_squared_error(
                    y_test_monthly[crime_type],
                    y_pred_monthly[crime_type]
                )
        ))
    print()
