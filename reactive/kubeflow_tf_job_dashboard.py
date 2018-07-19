from charms.reactive import set_flag
from charms.reactive import when, when_not

from charms import layer


@when_not('layer.docker-resource.tf-operator-image.fetched')
def fetch_image():
    layer.docker_resource.fetch('tf-operator-image')


@when('layer.docker-resource.tf-operator-image.fetched')
@when_not('charm.kubeflow-tf-job-dashboard.started')
def start_charm():
    layer.status.maintenance('configuring container')

    image_info = layer.docker_resource.get_info('tf-operator-image')

    layer.caas_base.pod_spec_set({
        'containers': [
            {
                'name': 'tf-job-dashboard',
                'imageDetails': {
                    'imagePath': image_info.registry_path,
                    'username': image_info.username,
                    'password': image_info.password,
                },
                'command': [
                    '/opt/tensorflow_k8s/dashboard/backend',
                ],
                'ports': [
                    {
                        'name': 'tf-dashboard',
                        'containerPort': 8080,
                    },
                ],
            },
        ],
    })

    layer.status.maintenance('creating container')
    set_flag('charm.kubeflow-tf-job-dashboard.started')
