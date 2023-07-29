# The official Mozilla Wiki. #Put a short project description here.
from pywikibot import family
class Family(family.Family):
	name = 'wikidebates'  # Set the family name; this should be the same as in the filename.
	langs = {
		'fr': 'fr.wikidebates.org',  # Put the hostname here.
	}

	# Translation used on all wikis for the different namespaces.
	# Most namespaces are inherited from family.Family.
	# Check the family.py file (in main directory) to see the standard
	# namespace translations for each known language.
	# You only need to enter translations that differ from the default.


	def scriptpath(self, code):
		return '/w'


	def protocol(self, code) -> str:
		"""Return 'https' as the protocol."""
		return 'https'
