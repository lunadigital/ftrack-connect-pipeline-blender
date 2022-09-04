# :coding: utf-8
# :copyright: Copyright (c) 2022 Luna Digital, Ltd.

import os
import sys
import ftrack_api
import logging
import functools

logger = logging.getLogger('ftrack_connect_pipeline_blender.discover')

plugin_base_dir = os.path.normpath(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
)
python_dependencies = os.path.join(plugin_base_dir, 'dependencies')
sys.path.append(python_dependencies)

def on_discover_pipeline_blender(session, event):
    from ftrack_connect_pipeline_blender import __version__ as integration_version

    data = {
        'integration': {
            'name': 'ftrack-connect-pipeline-blender',
            'version': integration_version
        }
    }

    return data

def on_launch_pipeline_blender(session, event):
    ''' Handle application launch and add environment to *event*. '''

    pipeline_blender_base_data = on_discover_pipeline_blender(session, event)

    blender_plugins_path = os.path.join(plugin_base_dir, 'resource', 'plugins')
    blender_script_path = os.path.join(plugin_base_dir, 'resource', 'scripts')

    # Discover plugins from definitions
    definitions_plugin_hook = os.getenv('FTRACK_DEFINITION_PLUGIN_PATH')
    plugin_hook = os.path.join(definitions_plugin_hook, 'blender', 'python')

    pipeline_blender_base_data['integration']['env'] = {
        'FTRACK_EVENT_PLUGIN_PATH.prepend': plugin_hook,
        'PYTHONPATH.prepend': os.path.pathsep.join(
            [python_dependencies, blender_script_path]
        ),
        'BLENDER_SCRIPT_PATH': blender_script_path,
        'BLENDER_PLUGIN_PATH.prepend': blender_plugins_path
    }

    selection = event['data'].get('context', {}).get('selection', [])

    if selection:
        task = session.get('Context', selection[0]['entityId'])

        env = pipeline_blender_base_data['integration']['env']
        custom_attributes = parent['custom_attributes']
        
        env['FS.set'] = custom_attributes.get('fstart', '1.0')
        env['FE.set'] = custom_attributes.get('fend', '100.0')
        env['FPS.set'] = custom_attributes.get('fps', '24.0')

    return pipeline_blender_base_data

def register(session):
    ''' Subscribe to application launch events on *registry*. '''
    if not isinstance(session, ftrack_api.session.Session):
        return

    handle_discovery_event = functools.partial(on_discover_pipeline_blender, session)

    session.event_hub.subscribe(
        'topic=ftrack.connect.application.discover and '
        'data.application.identifier=blender*'
        #' and data.application.version >= 3.0',
        handle_discovery_event,
        priority=40
    )

    handle_launch_event = functools.partial(on_launch_pipeline_blender, session)

    session.event_hub.subscribe(
        'topic=ftrack.connect.application.launch and '
        'data.application.identifier=blender*'
        #' and data.application.version >= 3.0',
        handle_launch_event,
        priority=40
    )