# frozen_string_literal: true

# MinkNote product blog: dated Markdown files in apps/minknote/blog/
# become pages at /apps/minknote/blog/<slug>/.
#
# Create a post with:
#   bundle exec ruby tools/minknote-post "My Post Title"

module MinknoteBlog
  POSTS_DIR = "apps/minknote/blog"
  URL_PREFIX = "/apps/minknote/blog"
  FILENAME_PATTERN = %r{\A#{Regexp.escape(POSTS_DIR)}/(\d{4}-\d{2}-\d{2})-(.+)\.(md|markdown|html)\z}

  module Permalink
    def self.apply(page)
      match = FILENAME_PATTERN.match(page.path.delete_prefix("/"))
      return unless match

      date_str, slug = match[1], match[2]
      page.data["date"] ||= Jekyll::Utils.parse_date("#{date_str} 00:00:00")
      page.data["permalink"] ||= "#{URL_PREFIX}/#{slug}/"
      page.data["layout"] ||= "minknote-post"
      page.data["minknote_blog"] = true
      page.data["hero_image"] = page.data["hero-image"] if page.data.key?("hero-image")
      page.data["show_hero"] = page.data["show-hero"] if page.data.key?("show-hero")
    end
  end
end

Jekyll::Hooks.register :pages, :post_init do |page|
  MinknoteBlog::Permalink.apply(page)
end
