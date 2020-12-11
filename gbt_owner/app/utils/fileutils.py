import globals
def crash_dump():
    print(f"Dumping Data: {globals.__RESULTS}")
    with open(f"DUMP-{globals.OUTPUTFILE}", "w+") as dp:
        dp.writelines([','.join([str(x) for x in r]) + '\n' for r in sorted(globals.__RESULTS, key=lambda row: row[0])])
        # dp.writelines([",".join([str(isbn), str(_old), str(_new)]) + '\n' for isbn,
        #                _old, _new in sorted(__RESULTS, key=lambda row: row[0])])
    print("Dump Complete.")


def write_part():
    with open(globals.OUTPUTFILE, "a") as fp:
        _tmp = globals.__RESULTS
        fp.writelines([ ",".join([str(x) for x in r]) + '\n' for r in sorted(_tmp, key=lambda row: row[0])])
        # fp.writelines([",".join([str(isbn), str(_old), str(_new)]) + '\n' for isbn,
        #                _old, _new in sorted(_tmp, key=lambda row: row[0])])
        for i, c in _tmp:
            for row in globals.__RESULTS:
                x, y = row
                if i == x:
                    globals.__RESULTS.remove(row)