#!/usr/bin/env python
import os
import copy
import argparse
import subprocess
import hashlib
import tempfile
import json
import xml.etree.ElementTree as ET
import logging
import pprint
from collections import defaultdict
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

COLOR_FUNCTION_TEMPLATE = """
function(feature, variableName, glyphObject, track) {{
    var score = {score};
    {opacity}
    return 'rgba({red}, {green}, {blue}, ' + opacity + ')';
}}
"""

COLOR_FUNCTION_TEMPLATE_QUAL = """
function(feature, variableName, glyphObject, track) {{

    var search_up = function self(sf, attr){
        if(sf.get(attr) !== undefined){
            return sf.get(attr);
        }
        if(sf.parent() === undefined) {
            return;
        }else{
            return self(sf.parent(), attr);
        }
    }

    var search_down = function self(sf, attr){
        if(sf.get(attr) !== undefined){
            return sf.get(attr);
        }
        if(sf.children() === undefined) {
            return;
        }else{
            for(var child_idx in sf.children()){
                var x = self(sf.children()[child_idx];
                if(x !== undefined){
                    return x;
                }
            }
            return;
        }
    }

    var color = (search_up(feature, 'color') || search_down(feature, 'color') || {user_spec_color});
    var score = (search_up(feature, 'score') || search_down(feature, 'score'));
    {opacity}
    return 'rgba({red}, {green}, {blue}, ' + opacity + ')';
}}
"""

BLAST_OPACITY_MATH = """
var opacity = 0;
if(score == 0.0) {
    opacity = 1;
} else{
    opacity = (20 - Math.log10(score)) / 180;
}
"""

BREWER_COLOUR_IDX = 0
BREWER_COLOUR_SCHEMES = [
    (166, 206, 227),
    (31, 120, 180),
    (178, 223, 138),
    (51, 160, 44),
    (251, 154, 153),
    (227, 26, 28),
    (253, 191, 111),
    (255, 127, 0),
    (202, 178, 214),
    (106, 61, 154),
    (255, 255, 153),
    (177, 89, 40)
    # (228, 26, 28),
    # (55, 126, 184),
    # (77, 175, 74),
    # (152, 78, 163),
    # (255, 127, 0),
]

BREWER_DIVERGING_PALLETES = {
    'BrBg': ("#543005", "#003c30"),
    'PiYg': ("#8e0152", "#276419"),
    'PRGn': ("#40004b", "#00441b"),
    'PuOr': ("#7f3b08", "#2d004b"),
    'RdBu': ("#67001f", "#053061"),
    'RdGy': ("#67001f", "#1a1a1a"),
    'RdYlBu': ("#a50026", "#313695"),
    'RdYlGn': ("#a50026", "#006837"),
    'Spectral': ("#9e0142", "#5e4fa2"),
}

# http://stackoverflow.com/questions/4296249/how-do-i-convert-a-hex-triplet-to-an-rgb-tuple-and-back
import struct
def rgb_from_hex(hexstr):
    return struct.unpack('BBB',hexstr.decode('hex'))


def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.iteritems():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


# score comes from feature._parent.get('score') or feature.get('score')
# Opacity math

TN_TABLE = {
    'gff3': '--gff',
    'gff': '--gff',
    'bed': '--bed',
    'genbank': '--gbk',
}

INSTALLED_TO = os.path.dirname(os.path.realpath(__file__))


class JbrowseConnector(object):

    def __init__(self, jbrowse, outdir, genomes, standalone=False, gencode=1):
        self.jbrowse = jbrowse
        self.outdir = outdir
        self.genome_paths = genomes
        self.brewer_colour_idx = 0
        self.standalone = standalone
        self.gencode = gencode

        if standalone:
            self.clone_jbrowse(self.jbrowse, self.outdir)
        else:
            try:
                os.makedirs(self.outdir)
            except OSError:
                # Ignore if the folder exists
                pass

        self.process_genomes()

    def subprocess_check_call(self, command):
        log.debug('cd %s && %s', self.outdir, ' '.join(command))
        subprocess.check_call(command, cwd=self.outdir)

    def _jbrowse_bin(self, command):
        return os.path.realpath(os.path.join(self.jbrowse, 'bin', command))

    def _get_colours(self):
        r, g, b = BREWER_COLOUR_SCHEMES[self.brewer_colour_idx]
        self.brewer_colour_idx += 1
        return r, g, b

    def process_genomes(self):
        for genome_path in self.genome_paths:
            self.subprocess_check_call([
                'perl', self._jbrowse_bin('prepare-refseqs.pl'),
                '--fasta', genome_path])

    def _add_json(self, json_data):
        if len(json_data.keys()) == 0:
            return

        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(json.dumps(json_data))
        tmp.close()
        cmd = ['perl', self._jbrowse_bin('add-track-json.pl'), tmp.name,
               os.path.join('data', 'trackList.json')]
        self.subprocess_check_call(cmd)
        os.unlink(tmp.name)

    def _add_track_json(self, json_data):
        if len(json_data.keys()) == 0:
            return

        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(json.dumps(json_data))
        tmp.close()
        cmd = ['perl', self._jbrowse_bin('add-track-json.pl'), tmp.name,
               os.path.join('data', 'trackList.json')]
        self.subprocess_check_call(cmd)
        os.unlink(tmp.name)

    def _min_max_gff(self, gff_file):
        min_val = None
        max_val = None
        with open(gff_file, 'r') as handle:
            for line in handle:
                try:
                    value = float(line.split('\t')[5])
                    min_val = min(value, (min_val or value))
                    max_val = max(value, (max_val or value))

                    if value < min_val:
                        min_val = value

                    if value > max_val:
                        max_val = value
                except Exception:
                    pass
        return min_val, max_val

    def _parse_colours(self, track):
        # Wiggle tracks have a bicolor pallete
        clientConfig = {}
        if track['format'] == 'wiggle':
            if track['style']['color_config'] == 'brewer':
                scheme = track['style']['color']
                if scheme not in BREWER_DIVERGING_PALLETES:
                    raise Exception("Unknown pallete")

                pos_color, neg_color = BREWER_DIVERGING_PALLETES[scheme]
            else:
                pos_color = track['style']['color_pos']
                neg_color = track['style']['color_neg']

            clientConfig['pos_color'] = pos_color
            clientConfig['neg_color'] = neg_color
        else:
            # Other tracks either use "__auto__" or specify a colour
            if track['style'].get('color', '__auto__') == '__auto__':
                # Automatically generate the next brewer colour
                red, green, blue = self._get_colours()
                clientConfig['color'] = 'rgba({red}, {green}, {blue}, 1)' \
                    .format(red=red, green=green, blue=blue)
            else:
                clientConfig['color'] = track['style']['color']
        return clientConfig

    def add_blastxml(self, data, trackData, **kwargs):
        gff3_unrebased = tempfile.NamedTemporaryFile(delete=False)
        cmd = ['python', os.path.join(INSTALLED_TO, 'blastxml_to_gapped_gff3.py'),
               '--trim_end', '--min_gap', str(kwargs['min_gap']), data]
        subprocess.check_call(cmd, cwd=self.outdir, stdout=gff3_unrebased)
        gff3_unrebased.close()

        gff3_rebased = tempfile.NamedTemporaryFile(delete=False)
        cmd = ['python', os.path.join(INSTALLED_TO, 'gff3_rebase.py')]
        if kwargs['protein']:
            cmd.append('--protein2dna')
        cmd.extend([kwargs['parent'], gff3_unrebased.name])
        subprocess.check_call(cmd, cwd=self.outdir, stdout=gff3_rebased)
        gff3_rebased.close()

        red, green, blue = self._get_colours()
        log.debug('RGB: %s %s %s', red, green, blue)
        log.debug(COLOR_FUNCTION_TEMPLATE)
        color_function = COLOR_FUNCTION_TEMPLATE.format(**{
            'score': "feature._parent.get('score')",
            'opacity': BLAST_OPACITY_MATH,
            'red': red,
            'green': green,
            'blue': blue,
        })
        log.debug(color_function)

        clientConfig = trackData['style']
        clientConfig['color'] = color_function.replace('\n', '')
        config = {'glyph': 'JBrowse/View/FeatureGlyph/Segments'}
        if 'category' in kwargs:
            config['category'] = kwargs['category']

        cmd = ['perl', self._jbrowse_bin('flatfile-to-json.pl'),
               '--gff', gff3_rebased.name,
               '--trackLabel', trackData['label'],
               '--key', trackData['key'],
               '--clientConfig', json.dumps(clientConfig),
               '--config', json.dumps(config),
               '--trackType', 'JBrowse/View/Track/CanvasFeatures'
               ]

        self.subprocess_check_call(cmd)
        os.unlink(gff3_rebased.name)
        os.unlink(gff3_unrebased.name)

    def add_bigwig(self, data, trackData, **kwargs):
        dest = os.path.join('data', 'raw', os.path.basename(data))
        cmd = ['ln', data, dest]
        self.subprocess_check_call(cmd)

        trackData.update({
            "urlTemplate": os.path.join('..', dest),
            "storeClass": "JBrowse/Store/SeqFeature/BigWig",
            "type": "JBrowse/View/Track/Wiggle/Density",
        })

        if 'bicolor_pivot' not in trackData:
            trackData['bicolor_pivot'] = kwargs['style'].get('bicolor_pivot', 'zero')

        if 'type' in kwargs:
            trackData['type'] = kwargs['type']

        if 'min' in kwargs and 'max' in kwargs:
            trackData['min'] = kwargs['min']
            trackData['max'] = kwargs['max']
        else:
            trackData['autoscale'] = kwargs.get('autoscale', 'local')

        self._add_track_json(trackData)

    def add_bam(self, data, trackData, **kwargs):
        dest = os.path.join('data', 'raw', os.path.basename(data))
        cmd = ['ln', '-s', data, dest]
        self.subprocess_check_call(cmd)

        bai_source = kwargs['bam_index']
        cmd = ['ln', '-s', bai_source, dest + '.bai']
        self.subprocess_check_call(cmd)

        trackData.update({
            "urlTemplate": os.path.join('..', dest),
            "type": "JBrowse/View/Track/Alignments2",
            "storeClass": "JBrowse/Store/SeqFeature/BAM",
        })

        if 'category' in kwargs:
            trackData['category'] = kwargs['category']

        self._add_track_json(trackData)

        if kwargs.get('auto_snp', False):
            trackData2 = copy.copy(trackData)
            trackData2.update({
                "type": "JBrowse/View/Track/SNPCoverage",
                "key": trackData['key'] + " - SNPs/Coverage",
                "label": trackData['label']  + "_autosnp",
            })

            self._add_track_json(trackData)

    def add_vcf(self, data, trackData, **kwargs):
        dest = os.path.join('data', 'raw', os.path.basename(data))
        # ln?
        cmd = ['ln', '-s', data, dest]
        self.subprocess_check_call(cmd)
        cmd = ['bgzip', dest]
        self.subprocess_check_call(cmd)
        cmd = ['tabix', '-p', 'vcf', dest + '.gz']
        self.subprocess_check_call(cmd)

        trackData.update({
            "urlTemplate": os.path.join('..', dest + '.gz'),
            "type": "JBrowse/View/Track/HTMLVariants",
            "storeClass": "JBrowse/Store/SeqFeature/VCFTabix",
        })
        self._add_track_json(trackData)

    def add_features(self, data, format, trackData, **kwargs):
        cmd = [
            'perl', self._jbrowse_bin('flatfile-to-json.pl'),
            TN_TABLE.get(format, 'gff'),
            data,
            '--trackLabel', trackData['label'],
            '--trackType', 'JBrowse/View/Track/CanvasFeatures',
            '--key', trackData['key']
        ]

        config = {}
        clientConfig = trackData['style']
        if 'category' in kwargs:
            config['category'] = kwargs['category']

        # Get min/max and build a scoring function since JBrowse doesn't
        min_val, max_val = self._min_max_gff(data)

        if min_val is not None and max_val is not None:
            MIN_MAX_OPACITY_MATH = """
            var opacity = (score - ({min})) * (1/(({max}) - ({min})));
            """.format(**{
                'max': max_val,
                'min': min_val,
            })

            red, green, blue = self._get_colours()
            if 'color' in clientConfig:
                if clientConfig['color'].startswith('#'):
                    red, green, blue = rgb_from_hex(clientConfig['color'][1:])

            color_function = COLOR_FUNCTION_TEMPLATE.format(**{
                'score': "feature.get('score')",
                'opacity': MIN_MAX_OPACITY_MATH,
                'red': red,
                'green': green,
                'blue': blue,
            })
        else:
            pass
            #if color in clientConfig:
            #(r, g, b) = rgb(mag)
            #color_function = COLOR_FUNCTION_TEMPLATE

        clientConfig['color'] = color_function.replace('\n', '')

        config['glyph'] = 'JBrowse/View/FeatureGlyph/Segments'

        cmd += ['--clientConfig', json.dumps(clientConfig),
                '--trackType', 'JBrowse/View/Track/CanvasFeatures'
                ]

        cmd.extend(['--config', json.dumps(config)])

        self.subprocess_check_call(cmd)

    def process_annotations(self, track):
        kwargs = {}
        outputTrackConfig = {}

        clientConfig = {
            'label':       track['style'].get('label', 'description'),
            'className':   track['style'].get('className', 'feature'),
            'description': track['style'].get('description', ''),
        }

        # Colour parsing is complex due to different track types having
        # different colour options.
        clientConfig.update(self._parse_colours(track))

        # Load clientConfig into outputTrackConfig
        outputTrackConfig['style'] = clientConfig

        log.debug('Track\n' + pprint.pformat(track))
        for i, (dataset_path, dataset_ext, track_human_label) in enumerate(track['trackfiles']):
            outputTrackConfig['key'] = track_human_label
            outputTrackConfig['label'] = hashlib.md5(dataset_path).hexdigest() + '_%s' % i

            # If a list of indices are available, set a variable with just the correct one.
            if 'bam_indexes' in track:
                kwargs['bam_index'] = track['bam_indexes'][i]

            log.debug('outputTrackConfig\n' + pprint.pformat(outputTrackConfig))
            log.debug('kwargs\n' + pprint.pformat(kwargs))

            if dataset_ext in ('gff', 'gff3', 'bed'):
                self.add_features(dataset_path, dataset_ext, outputTrackConfig, **kwargs)
            #elif dataset_ext == 'bigwig':
                #self.add_bigwig(dataset, outputTrackConfig, **kwargs)
            #elif dataset_ext == 'bam':
                #self.add_bam(dataset, outputTrackConfig, **kwargs)
            #elif dataset_ext == 'blastxml':
                #self.add_blastxml(dataset, outputTrackConfig, **kwargs)
            #elif dataset_ext == 'vcf':
                #self.add_vcf(dataset, outputTrackConfig, **kwargs)

    def clone_jbrowse(self, jbrowse_dir, destination):
        """Clone a JBrowse directory into a destination directory.
        """
        # JBrowse seems to have included some bad symlinks, cp ignores bad symlinks
        # unlike copytree
        cmd = ['rsync', '-r', os.path.join(jbrowse_dir, ''), destination]
        subprocess.check_call(cmd)
        cmd = ['mkdir', '-p', os.path.join(destination, 'data', 'raw')]
        subprocess.check_call(cmd)

        # http://unix.stackexchange.com/a/38691/22785
        # JBrowse releases come with some broken symlinks
        cmd = ['find', destination, '-type', 'l', '-xtype', 'l', '-exec', 'rm', "'{}'", '+']
        subprocess.check_call(cmd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="", epilog="")
    parser.add_argument('xml', type=file, help='Track Configuration')

    parser.add_argument('--jbrowse', help='Folder containing a jbrowse release')
    parser.add_argument('--outdir', help='Output directory', default='out')
    parser.add_argument('--standalone', help='Standalone mode includes a copy of JBrowse', action='store_true')
    args = parser.parse_args()

    tree = ET.parse(args.xml.name)
    root = tree.getroot()

    jc = JbrowseConnector(
        jbrowse=args.jbrowse,
        outdir=args.outdir,
        genomes=[os.path.realpath(x.text) for x in root.findall('metadata/genomes/genome')],
        standalone=args.standalone,
        gencode=root.find('metadata/gencode').text
    )

    for track in root.findall('tracks/track'):
        track_conf = {}
        track_conf['trackfiles'] = [
            (os.path.realpath(x.attrib['path']), x.attrib['ext'], x.attrib['label'])
            for x in track.findall('files/trackFile')
        ]

        track_conf['category'] = track.attrib['cat']
        track_conf['format'] = track.attrib['format']
        track_conf['style'] = {t.tag: t.text for t in track.find('options/style')}
        track_conf['conf'] = etree_to_dict(track.find('options'))

        extra = {}
        if 'options' in track_conf['conf']:
            if 'pileup' in track_conf['conf']:
                if 'bam_indices' in track_conf['conf']['pileup']:
                    corrected = []
                    if isinstance(track_conf['conf']['pileup']['bam_indices']['bam_index'], list):
                        for bam_index in track_conf['conf']['pileup']['bam_indices']['bam_index']:
                            corrected.append(os.path.realpath(bam_index))
                    else:
                        corrected.append(os.path.realpath(track_conf['conf']['pileup']['bam_indices']['bam_index']))
                    track_conf['conf']['pileup']['bam_indices'] = corrected
            elif 'blast' in track_conf['conf']:
                if 'parent' in track_conf['conf']['blast']:
                    track_conf['conf']['blast']['parent'] = os.path.realpath(track_conf['conf']['blast']['parent'])

        log.debug('Parsed Track: \n%s', pprint.pformat(track_conf))

        jc.process_annotations(track_conf)
