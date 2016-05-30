import os
import json
from unittest import TestCase


from click.testing import CliRunner

from container_transform.client import transform


class ClientTests(TestCase):
    """
    Tests for client
    """
    def setUp(self):
        self.yaml_input = (
            '\n'
            'web:\n'
            '  image: me/myapp\n'
            '  mem_limit: 1024b\n'
            '\n'
            'web2:\n'
            '  build: .\n'
            '  mem_limit: 1024b\n'
        )

    def test_prompt_compose_quiet(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('docker-compose.yml', 'w') as f:
                f.write(self.yaml_input)

            result = runner.invoke(transform, ['docker-compose.yml', '-q'])
            assert result.exit_code == 0

            data = json.loads(result.output)
            self.assertIn(
                {
                    'name': 'web',
                    'image': 'me/myapp',
                    'memory': 4,
                    'essential': True
                },
                data['containerDefinitions'],
            )
            self.assertIn(
                {
                    'name': 'web2',
                    'memory': 4,
                    'essential': True
                },
                data['containerDefinitions'],
            )

    def test_prompt_fig_quiet(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('fig.yml', 'w') as f:
                f.write(self.yaml_input)

            result = runner.invoke(transform, ['fig.yml', '-q'])
            assert result.exit_code == 0

            data = json.loads(result.output)

            self.assertIn(
                {
                    'name': 'web',
                    'image': 'me/myapp',
                    'memory': 4,
                    'essential': True
                },
                data['containerDefinitions'],
            )
            self.assertIn(
                {
                    'name': 'web2',
                    'memory': 4,
                    'essential': True
                },
                data['containerDefinitions'],
            )

    def test_prompt_fig_no_quiet(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('fig.yml', 'w') as f:
                f.write(self.yaml_input)

            result = runner.invoke(transform, ['fig.yml', '--no-verbose'])
            assert result.exit_code == 0

            data = json.loads(result.output.split('\n')[0])

            messages = set(result.output.split('\n')[1:])

            self.assertEqual(
                {'Container web2 is missing required parameter "image".',
                 ''},
                messages
            )

            self.assertIn(
                {
                    'name': 'web',
                    'image': 'me/myapp',
                    'memory': 4,
                    'essential': True
                },
                data['containerDefinitions'],
            )
            self.assertIn(
                {
                    'name': 'web2',
                    'memory': 4,
                    'essential': True
                },
                data['containerDefinitions'],
            )

    def test_prompt_compose_systemd_quiet(self):
        runner = CliRunner()

        input_file = '{}/docker-compose-web.yml'.format(os.path.dirname(__file__))

        result = runner.invoke(transform, [input_file, '-q', '--output-type', 'systemd'])
        assert result.exit_code == 0

        service_file = '{}/web.service'.format(os.path.dirname(__file__))
        service_contents = open(service_file).read()
        self.assertEqual(
            result.output,
            service_contents
        )

    def test_prompt_marathon_compose_quiet(self):
        runner = CliRunner()

        input_file = '{}/marathon-test.json'.format(os.path.dirname(__file__))

        result = runner.invoke(
            transform,
            [input_file, '-q', '--input-type', 'marathon', '--output-type', 'compose'])
        assert result.exit_code == 0

        service_file = '{}/marathon-test-out.yaml'.format(os.path.dirname(__file__))
        service_contents = open(service_file).read()
        self.assertEqual(
            result.output,
            service_contents
        )

    def test_prompt_marathon_compose_group_quiet(self):
        runner = CliRunner()

        input_file = '{}/marathon-group.json'.format(os.path.dirname(__file__))

        result = runner.invoke(
            transform,
            [input_file, '-q', '--input-type', 'marathon', '--output-type', 'compose'])
        assert result.exit_code == 0

        service_file = '{}/marathon-group-out.yaml'.format(os.path.dirname(__file__))
        service_contents = open(service_file).read()
        self.assertEqual(
            result.output,
            service_contents
        )

    def test_prompt_marathon_compose_list_quiet(self):
        runner = CliRunner()

        input_file = '{}/marathon-list.json'.format(os.path.dirname(__file__))

        result = runner.invoke(
            transform,
            [input_file, '-q', '--input-type', 'marathon', '--output-type', 'compose'])
        assert result.exit_code == 0

        service_file = '{}/marathon-list-out.yaml'.format(os.path.dirname(__file__))
        service_contents = open(service_file).read()
        self.assertEqual(
            result.output,
            service_contents
        )

    def test_prompt_compose_marathon_quiet(self):
        runner = CliRunner()
        input_file = '{}/marathon-test.yaml'.format(os.path.dirname(__file__))

        result = runner.invoke(
            transform,
            [input_file, '-q', '--input-type', 'compose', '--output-type', 'marathon'])
        assert result.exit_code == 0

        service_file = '{}/marathon-compose-out.json'.format(os.path.dirname(__file__))
        service_contents = open(service_file).read()
        self.assertEqual(
            result.output,
            service_contents
        )

    def test_prompt_compose_marathon_quiet_mini(self):
        runner = CliRunner()
        self.maxDiff = None
        input_file = '{}/marathon-test.yaml'.format(os.path.dirname(__file__))

        result = runner.invoke(
            transform,
            [
                input_file, '-q', '--input-type', 'compose',
                '--output-type', 'marathon', '--no-verbose'])
        assert result.exit_code == 0

    def test_prompt_compose_marathon_single_app_quiet(self):
        runner = CliRunner()
        self.maxDiff = None
        input_file = '{}/composev2.yml'.format(os.path.dirname(__file__))

        result = runner.invoke(
            transform,
            [
                input_file, '-q', '--input-type', 'compose',
                '--output-type', 'marathon', '--no-verbose'])
        assert result.exit_code == 0
        result_data = json.loads(result.output)
        self.assertIsInstance(result_data, dict)
