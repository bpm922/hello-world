import re
import logging
from typing import List, Optional
from core.plugin_base import PluginBase, SearchType, PluginResult


class PhoneNumberPlugin(PluginBase):
    """
    Phone number validation and parsing plugin.
    Validates format and extracts country code information.
    """
    
    def __init__(self):
        super().__init__()
        self.country_codes = self._load_country_codes()

    @property
    def name(self) -> str:
        return "Phone Number Lookup"

    @property
    def description(self) -> str:
        return "Phone number validation and country code identification"

    @property
    def supported_search_types(self) -> List[SearchType]:
        return [SearchType.PHONE]

    def _load_country_codes(self) -> dict:
        """Load common country calling codes"""
        return {
            '1': 'United States/Canada',
            '7': 'Russia/Kazakhstan',
            '20': 'Egypt',
            '27': 'South Africa',
            '30': 'Greece',
            '31': 'Netherlands',
            '32': 'Belgium',
            '33': 'France',
            '34': 'Spain',
            '36': 'Hungary',
            '39': 'Italy',
            '40': 'Romania',
            '41': 'Switzerland',
            '43': 'Austria',
            '44': 'United Kingdom',
            '45': 'Denmark',
            '46': 'Sweden',
            '47': 'Norway',
            '48': 'Poland',
            '49': 'Germany',
            '51': 'Peru',
            '52': 'Mexico',
            '53': 'Cuba',
            '54': 'Argentina',
            '55': 'Brazil',
            '56': 'Chile',
            '57': 'Colombia',
            '58': 'Venezuela',
            '60': 'Malaysia',
            '61': 'Australia',
            '62': 'Indonesia',
            '63': 'Philippines',
            '64': 'New Zealand',
            '65': 'Singapore',
            '66': 'Thailand',
            '81': 'Japan',
            '82': 'South Korea',
            '84': 'Vietnam',
            '86': 'China',
            '90': 'Turkey',
            '91': 'India',
            '92': 'Pakistan',
            '93': 'Afghanistan',
            '94': 'Sri Lanka',
            '95': 'Myanmar',
            '98': 'Iran',
            '212': 'Morocco',
            '213': 'Algeria',
            '216': 'Tunisia',
            '218': 'Libya',
            '220': 'Gambia',
            '234': 'Nigeria',
            '237': 'Cameroon',
            '254': 'Kenya',
            '255': 'Tanzania',
            '256': 'Uganda',
            '351': 'Portugal',
            '353': 'Ireland',
            '354': 'Iceland',
            '358': 'Finland',
            '370': 'Lithuania',
            '371': 'Latvia',
            '372': 'Estonia',
            '380': 'Ukraine',
            '420': 'Czech Republic',
            '421': 'Slovakia',
            '852': 'Hong Kong',
            '853': 'Macau',
            '886': 'Taiwan',
            '960': 'Maldives',
            '961': 'Lebanon',
            '962': 'Jordan',
            '963': 'Syria',
            '964': 'Iraq',
            '965': 'Kuwait',
            '966': 'Saudi Arabia',
            '967': 'Yemen',
            '968': 'Oman',
            '970': 'Palestine',
            '971': 'United Arab Emirates',
            '972': 'Israel',
            '973': 'Bahrain',
            '974': 'Qatar',
            '975': 'Bhutan',
            '976': 'Mongolia',
            '977': 'Nepal',
        }

    def run_search(self, query: str, search_type: SearchType) -> PluginResult:
        if search_type != SearchType.PHONE:
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=f"Unsupported search type: {search_type.value}"
            )

        try:
            logging.info(f"Analyzing phone number: {query}")
            
            cleaned_number = self._clean_phone_number(query)
            
            analysis = {
                'original': query,
                'cleaned': cleaned_number,
                'is_valid_format': False,
                'country_code': None,
                'country': None,
                'national_number': None,
                'is_international_format': False
            }
            
            if self._is_valid_phone_format(cleaned_number):
                analysis['is_valid_format'] = True
                
                country_code = self._extract_country_code(cleaned_number)
                if country_code:
                    analysis['country_code'] = country_code
                    analysis['country'] = self.country_codes.get(country_code, 'Unknown')
                    analysis['is_international_format'] = True
                    
                    national_number = cleaned_number[len(country_code):]
                    analysis['national_number'] = national_number
            
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=True,
                data=analysis,
                metadata={
                    'format_valid': analysis['is_valid_format'],
                    'total_digits': len(re.sub(r'\D', '', cleaned_number))
                }
            )
            
        except Exception as e:
            logging.error(f"Phone number analysis error: {e}")
            return PluginResult(
                plugin_name=self.name,
                search_type=search_type,
                query=query,
                success=False,
                error=f"Analysis failed: {str(e)}"
            )

    def _clean_phone_number(self, phone: str) -> str:
        """Remove all non-digit characters except leading +"""
        if phone.startswith('+'):
            return '+' + re.sub(r'\D', '', phone)
        return re.sub(r'\D', '', phone)

    def _is_valid_phone_format(self, phone: str) -> bool:
        """Check if phone number has valid format"""
        digits = re.sub(r'\D', '', phone)
        
        return 7 <= len(digits) <= 15

    def _extract_country_code(self, phone: str) -> Optional[str]:
        """Extract country code from international format phone number"""
        if not phone.startswith('+'):
            return None
        
        digits = phone[1:]
        
        for length in [3, 2, 1]:
            code = digits[:length]
            if code in self.country_codes:
                return code
        
        return None
