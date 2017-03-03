#!/bin/env python

# Copyright 2017, Fabien Boucher
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import glob
import shutil
import tarfile
import zipfile
import tempfile
import argparse
import requests

archives = {
    # No release. Master of 03/05/2017
    "simplePagination": "https://github.com/flaviusmatis/simplePagination.js/archive/07c37285fafc7dbabce0392f730037ac012cc3ea.tar.gz",  # noqa
    "moment.js": "https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.17.1/moment.min.js",  # noqa
    "d3.js": "https://cdnjs.cloudflare.com/ajax/libs/d3/3.1.6/d3.min.js",  # noqa
    "jquery-ui": "https://jqueryui.com/resources/download/jquery-ui-1.12.1.zip",  # noqa
    "jquery": "https://cdnjs.cloudflare.com/ajax/libs/jquery/1.12.4/jquery.min.js",  # noqa
    "dimple.js": "https://cdnjs.cloudflare.com/ajax/libs/dimple/2.2.0/dimple.latest.min.js",  # noqa
    "bootstrap": "https://github.com/twbs/bootstrap/releases/download/v3.3.7/bootstrap-3.3.7-dist.zip"  # noqa
}


def download_file(url, targetdir):
    local_filename = url.split('/')[-1]
    local_filename = os.path.join(targetdir, local_filename)
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return local_filename


def install_archive(name, path, basepath):
    if name == "moment.js":
        shutil.move(path,
                    os.path.join(basepath, 'javascript', 'moment.min.js'))
    elif name == "simplePagination":
        tar = tarfile.open(path)
        tar.extractall(os.path.dirname(path))
        tar.close()
        shutil.move(
            os.path.join(
                os.path.dirname(path),
                "simplePagination.js-07c37285fafc7dbabce0392f730037ac012cc3ea",
                "jquery.simplePagination.js"),
            os.path.join(basepath, 'javascript', 'jquery.simplePagination.js')
            )
        shutil.move(
            os.path.join(
                os.path.dirname(path),
                "simplePagination.js-07c37285fafc7dbabce0392f730037ac012cc3ea",
                "simplePagination.css"),
            os.path.join(basepath, 'css', 'simplePagination.css')
            )
        shutil.rmtree(os.path.join(
            os.path.dirname(path),
            "simplePagination.js-07c37285fafc7dbabce0392f730037ac012cc3ea"))
        os.unlink(path)
    elif name == "d3.js":
        shutil.move(path,
                    os.path.join(basepath, 'javascript', 'd3.min.js'))
    elif name == "jquery":
        shutil.move(path,
                    os.path.join(basepath, 'javascript', 'jquery.min.js'))
    elif name == "dimple.js":
        shutil.move(path,
                    os.path.join(basepath, 'javascript', 'dimple.min.js'))
    elif name == "jquery-ui":
        zi = zipfile.ZipFile(path)
        zi.extractall(os.path.dirname(path))
        zi.close()
        shutil.move(
            os.path.join(os.path.dirname(path),
                         "jquery-ui-1.12.1",
                         "jquery-ui.min.js"),
            os.path.join(basepath, 'javascript', 'jquery-ui.min.js')
            )
        shutil.move(
            os.path.join(os.path.dirname(path),
                         "jquery-ui-1.12.1",
                         "jquery-ui.min.css"),
            os.path.join(basepath, 'css', 'jquery-ui.min.css')
            )
        for f in glob.glob(os.path.join(os.path.dirname(path),
                           "jquery-ui-1.12.1", "images", "*")):
            shutil.move(f, os.path.join(basepath,
                                        'images', os.path.basename(f)))
        shutil.rmtree(os.path.join(os.path.dirname(path), "jquery-ui-1.12.1"))
        os.unlink(path)
    elif name == "bootstrap":
        zi = zipfile.ZipFile(path)
        zi.extractall(os.path.dirname(path))
        zi.close()
        shutil.move(
            os.path.join(os.path.dirname(path),
                         "bootstrap-3.3.7-dist", "js",
                         "bootstrap.min.js"),
            os.path.join(basepath, 'javascript', 'bootstrap.min.js')
            )
        shutil.move(
            os.path.join(os.path.dirname(path),
                         "bootstrap-3.3.7-dist", "css",
                         "bootstrap.min.css"),
            os.path.join(basepath, 'css', 'bootstrap.min.css')
            )
        for f in glob.glob(os.path.join(os.path.dirname(path),
                           "bootstrap-3.3.7-dist", "fonts", "*")):
            shutil.move(f, os.path.join(basepath,
                                        'fonts', os.path.basename(f)))
        shutil.rmtree(
            os.path.join(os.path.dirname(path), "bootstrap-3.3.7-dist"))
        os.unlink(path)
    else:
        print "Install for %s not supported. skip." % name


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Fetch web assets for repoXplorer.')
    parser.add_argument(
        '-p', '--path', type=str,
        default=os.path.join(sys.prefix, 'local/share/repoxplorer/public/'),
        help='Install path')

args = parser.parse_args()
td = tempfile.mkdtemp()
print "Assets will be installed in %s ..." % args.path
print "Fetch/Deflate assets in a temp directory %s ..." % td
for d in ('css', 'javascript', 'images', 'fonts'):
    os.mkdir(os.path.join(td, d))
for name, url in archives.items():
    print "Fetch and Install %s ..." % name
    path = download_file(url, td)
    install_archive(name, path, td)

# Copy already install repoxplorer bundled assets if exists
if os.path.exists(os.path.join(args.path, 'javascript', 'repoxplorer.js')):
    shutil.copy(os.path.join(args.path, 'javascript', 'repoxplorer.js'),
                os.path.join(td, 'javascript', 'repoxplorer.js'))
    print "Copied repoxplorer.js"
if os.path.exists(os.path.join(args.path, 'css', 'repoxplorer.css')):
    shutil.copy(os.path.join(args.path, 'css', 'repoxplorer.css'),
                os.path.join(td, 'css', 'repoxplorer.css'))
    print "Copied repoxplorer.css"

shutil.rmtree(args.path)
shutil.move(td, args.path)
print "Assets moved to %s" % args.path
