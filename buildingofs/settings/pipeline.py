PIPELINE_TEMPLATE_EXT = '.ejs'
PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.yuglify.YuglifyCompressor'
PIPELINE_JS_COMPRESSOR = None
PIPELINE_COMPILERS = (
    'pipeline.compilers.sass.SASSCompiler',
)

PIPELINE_DISABLE_WRAPPER = True

PIPELINE_CSS = {
    'base_styles': {
        'source_filenames': (
            'styles/src/base.scss',
        ),
        'output_filename': '/compiled/styles/base.css',
        #'extra_context': {
        #    'media': 'screen,projection',
        #},
    },
}

#PIPELINE_JS = {
#    'base_libs': {
#        'source_filenames': (
#            'scripts/build/common.js',
#            'scripts/build/components/init.js',
#        ),
#        'output_filename': 'compiled/scripts/common.js',
#    },
#}
