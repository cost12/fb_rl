import nfl_data_py as nfl


def main():
    data = nfl.import_seasonal_data([2023])
    print(data.columns)

    data = nfl.import_pbp_data([2023])
    print(data.columns)

    data = nfl.import_weekly_data([2023])
    print(data.columns)

    data = nfl.import_ngs_data('receiving')
    print(data.columns)

    data = nfl.import_ngs_data('passing')
    print(data.columns)

    data = nfl.import_ngs_data('rushing')
    print(data.columns)

    data = nfl.import_snap_counts([2023])
    print(data.columns)

if __name__=="__main__":
    main()