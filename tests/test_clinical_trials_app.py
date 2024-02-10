import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from clinical_trials_app import fetch_studies, process_studies

class TestFetchStudies(unittest.TestCase):
    @patch('clinical_trials_app.requests.get')
    def test_fetch_studies(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'id': 1, 'title': 'Study 1'}, {'id': 2, 'title': 'Study 2'}, {'id': 3, 'title': 'Study 3'}]
        mock_get.return_value = mock_response
        condition = 'test condition'
        term = 'test term'
        location = 'test location'
        status = 'test status'
        min_age = '0'
        max_age = '100'

        result = fetch_studies(condition, term, location, status, min_age, max_age)
        expected_result = [{'id': 1, 'title': 'Study 1'}, {'id': 2, 'title': 'Study 2'}, {'id': 3, 'title': 'Study 3'}]
        self.assertEqual(result, expected_result)



class TestProcessStudies(unittest.TestCase):
    def test_process_studies(self):
        data = {
            'studies': [
                {
                    'protocolSection': {
                        'identificationModule': {'briefTitle': 'Test Study', 'nctId': 'NCT123456'},
                        'designModule': {'phases': ['Phase 1', 'Phase 2']},
                        'eligibilityModule': {'eligibilityCriteria': 'Test Criteria'},
                        'contactsLocationsModule': {
                            'centralContacts': [{'name': 'Test Name', 'role': 'Test Role', 'phone': '1234567890', 'email': 'test@example.com'}],
                            'locations': [{'facility': 'Test Facility', 'city': 'Test City', 'state': 'Test State', 'country': 'Test Country'}]
                        }
                    }
                }
            ]
        }
        result = process_studies(data)
        expected_result = pd.DataFrame(
            [
                [
                    'Test Study',
                    'Phase 1, Phase 2',
                    'Test Criteria',
                    'https://clinicaltrials.gov/ct2/show/NCT123456',
                    'Test Facility',
                    'Name: Test Name, Role: Test Role, Phone: 1234567890, Email: test@example.com',
                    ''
                ]
            ],
            columns=['Title', 'Phase', 'Eligibility Criteria', 'Link to Study', 'Primary Location', 'Primary Contact', 'Additional Locations and Contacts']
        )
        pd.testing.assert_frame_equal(result, expected_result)

if __name__ == '__main__':
    unittest.main()