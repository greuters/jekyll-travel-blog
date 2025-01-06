import os
import argparse
import logging
import re
import csv
from datetime import datetime
from pathlib import Path
from lxml import etree as etree

# TODO:
# - integrate wpt cleaning for locus tracks
FILENAME_PATTERN = '^GPSlog_(?P<trackNumber>\d{4}).*\((?P<dateString>[0123]\d [A-Z][a-z][a-z] \d{4}).*\)\.(?P<ext>txt|gpx|csv)$'

def parse_filename(name):
    m = re.compile(FILENAME_PATTERN).match(name)
    if m is None:
        raise Exception(
            f"filename {name} doesn't match regex {FILENAME_PATTERN}")
    return m

def compute_highres(trackPath):
    """
    :param trackPath: path of the track file
    :type trackPath: :class:`pathlib.Path`
    :return: path of output
    :rtype: :class:`pathlib.Path`
    """
    outputPath = outputDir / trackPath.with_suffix('.gpx').name

    match parse_filename(trackPath.name).group('ext'):
        case 'gpx':
            # GPX from some routing app
            # keep only tracks and simplify
            cmd = f'gpsbabel -i gpx -f "{trackPath}" ' + \
                '-x nuketypes,waypoints,routes ' + \
                '-x position,distance=50m -x simplify,crosstrack,error=0.01k ' + \
                f'-o gpx,gpxver=1.1 -F "{outputPath}"'
            logging.info(cmd)
            os.system(cmd)

        case 'txt':
            # assuming NMEA file, simplify and convert
            cmd = f'gpsbabel -i nmea -f "{trackPath}" ' + \
                '-x position,distance=50m -x simplify,crosstrack,error=0.01k ' + \
                f'-o gpx,gpxver=1.1 -F "{outputPath}"'
            logging.info(cmd)
            os.system(cmd)

        case 'csv':
            templatePath = Path('template.gpx')
            gpx_ns = {'GPX': 'http://www.topografix.com/GPX/1/1'}
            parser = etree.XMLParser(remove_blank_text=True)
            tree = etree.parse(templatePath, parser)
            trkseg = tree.find('GPX:trk/GPX:trkseg', gpx_ns)
            with open(trackPath) as fin:
                reader = csv.reader(fin)
                for coordinates in reader:
                    rawLatitude = coordinates[0].strip().split('.')
                    rawLongitude = coordinates[1].strip().split('.')
                    latitude = int(rawLatitude[0]) + int(rawLatitude[1]) / 600
                    longitude = int(rawLongitude[0]) + int(rawLongitude[1]) / 600
                    trkseg.append(etree.XML(f'<trkpt lat="{latitude}" lon="-{longitude}"/>'))
            tree.write(outputPath, pretty_print=True)

        case fileType:
            raise Exception(
                    f"'{trackPath}' has unknown file type '{fileType}'")

    return outputPath

def compute_lowres(highresPath):
    """
    :param highresPath: path of the high resolution gpx track file to convert
    :type highresPath: :class:`pathlib.Path`
    """
    lowresPath = outputDir / highresPath.name.replace('highres', 'lowres')
    if lowresPath.exists():
        logging.info(f'omit regenerating existing {lowresPath}')
    else:
        cmd = f'gpsbabel -i gpx -f "{highresPath}" ' + \
            '-x position,distance=1000m -x simplify,crosstrack,error=0.9k ' + \
            f'-o gpx,gpxver=1.1 -F "{lowresPath}"'
        logging.info(cmd)
        os.system(cmd)

def merge_tracks(trackPaths, outputPath):
    """
    :param trackPaths: list of paths of gpx track files to be merged
    :type trackPaths: list of :class:`pathlib.Path`
    :param trackPaths: path of the merged track
    :type trackPaths: :class:`pathlib.Path`
    """
    cmd = f'gpsbabel -i gpx '
    for trackPath in trackPaths:
        cmd += f'-f "{trackPath}" '
    cmd += '-x track,trk2seg '
    cmd += f'-o gpx,gpxver=1.1 -F "{outputPath}"'
    logging.info(cmd)
    os.system(cmd)

    for trackPath in trackPaths:
        trackPath.unlink()

def convert_tracks(firstTrackNumber, trackDir, vehicle, outputDir):
    """
    Convert input NMEA .txt, .csv and .gpx files to lowres and highres gpx tracks

    Files are processed in alphabetical order, input files from the same day
    are merged, the output files are consecutively numbered and vehicle type is
    appended to the name.

    :param firstTrackNumber: number to assign to the first track
    :type firstTrackNumber: int
    :param trackDir: path to the directory containing NMEA .txt files
    :type trackDir: :class:`pathlib.Path`
    :param vehicle: means of transport to write as name of the gpx track
    :type vehicle: str
    :param outputDir: path to the directory where generated files are written
    :type outputDir: :class:`pathlib.Path`
    :return: track number following the last processed track
    :rtype: int
    """
    processedDates = set()
    outputTrackNumber = firstTrackNumber
    for trackPath in sorted(trackDir.glob('*')):
        inputDate = parse_filename(trackPath.name).group('dateString')
        if inputDate in processedDates:
            continue
        processedDates.add(inputDate)

        outputDate = datetime.strftime(datetime.strptime(inputDate, '%d %b %Y'), '%Y-%m-%d')
        highresPath = outputDir / f'{outputTrackNumber:>04}_{outputDate}_{vehicle}_highres.gpx'
        outputTrackNumber += 1
        if highresPath.exists():
            logging.info(f'omit regenerating existing {highresPath}')
            continue

        partOutputPaths = []
        for partPath in sorted(trackDir.glob(f'*{inputDate}*')):
            partOutputPaths.append(compute_highres(partPath))

        assert(len(partOutputPaths) > 0)
        if len(partOutputPaths) == 1:
            logging.info(f'rename {partOutputPaths[0]} to {highresPath}')
            partOutputPaths[0].rename(highresPath)
        else:
            merge_tracks(partOutputPaths, highresPath)

    for highresPath in sorted(outputDir.glob('*_highres.gpx')):
        compute_lowres(highresPath)

    return outputTrackNumber

if __name__== "__main__":
    logging.basicConfig(level=logging.INFO)

    validVehicles = ['bicycle', 'fossil', 'sail']
    parser = argparse.ArgumentParser(description=
        f'''Convert NMEA .txt files from CALogger and .gpx files to low and
        high resolution gpx tracks;
        filenames should match the following regex: {FILENAME_PATTERN}
        input sub-directory names should be ordered and have a valid vehicle
        (one of "{validVehicles}") as suffix, separated by an underscore
        ''')
    parser.add_argument('--inputDir',
            default='input',
            help=f'''input directory with NMEA and/or.gpx files stored in
            ordered subdirectories. Each subdirectory should have a valid vehicle name
            as suffix, separated by an underscore.\n
            Example: 'input/01_mexico_{validVehicles[0]}'
            allowed suffixes / vehicles: {validVehicles}''')
    parser.add_argument('--outputDir',
            default='output',
            help='output directory to write generated tracks to')
    args = parser.parse_args()

    inputDir = Path(args.inputDir)
    outputDir = Path(args.outputDir)
    outputTrackNumber = 0
    for trackDir in sorted(inputDir.iterdir()):
        if not trackDir.is_dir():
            continue
        vehicle = trackDir.name.split('_')[-1]
        if vehicle not in validVehicles:
            raise Exception(f'invalid vehicle: "{vehicle}" of {trackDir}')
        outputTrackNumber = convert_tracks(outputTrackNumber, trackDir, vehicle, outputDir)
