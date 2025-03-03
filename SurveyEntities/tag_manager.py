import copy
from typing import List

from SurveyEntities.image_tag import ImageTag


class TagManager:

    def __init__(self, tags: List[ImageTag] = None):
        self.tags = tags or []

    def __repr__(self):
        return self.tags

    def get_matching_tag(self, tag):
        matching_tags = [matching_tag for matching_tag in self.tags if matching_tag.name == tag.name]
        num_matches = len(matching_tags)
        if num_matches == 0:
            return None
        if num_matches == 1:
            return matching_tags[0]
        if len(matching_tags) > 1:
            raise Exception(f"Found duplicate tags [{tag.name}]")

    def apply_tag(self, tag: ImageTag, *args):
        matching_tag = self.get_matching_tag(tag)
        if matching_tag is None:
            self.add_tag(tag)
        elif tag.state is True:
            self.update_tag(tag, matching_tag)
        elif tag.state is False:
            self.remove_tag(matching_tag)

    def update_tag(self, new_tag, current_tag):
        print(f"Updated Tag: {current_tag.name}")
        tag_index = self.tags.index(current_tag)
        self.tags[tag_index] = new_tag

    def add_tag(self, tag):
        print(f"Added Tag: {tag.name}")
        self.tags.append(copy.deepcopy(tag))

    def remove_tag(self, tag):
        print(f"Removed Tag: {tag.name}")
        self.tags.remove(tag)
