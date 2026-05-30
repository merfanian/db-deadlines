# coding: utf-8
# Generate per-subject JSON API endpoints from conference YAML data
# Produces: /api/{SUB}.json for each subject tag

require 'json'

module Jekyll
  class SubjectJsonPage < Page
    def initialize(site, base, sub_code, conferences)
      @site = site
      @base = base
      @dir  = 'api'
      @name = "#{sub_code}.json"

      self.process(@name)
      self.content = JSON.generate(conferences)
      self.data = {
        'layout' => nil,
        'title'  => "#{sub_code} Conferences"
      }
    end
  end

  class ApiJsonGenerator < Generator
    safe true
    priority :low

    def generate(site)
      # Collect all conferences from _data/conferences/*.yml
      all_conferences = []
      if site.data['conferences']
        site.data['conferences'].each do |_filename, entries|
          next unless entries.is_a?(Array)
          entries.each do |entry|
            all_conferences << entry if entry.is_a?(Hash) && entry['id']
          end
        end
      end

      # Collect all unique subject tags
      all_subs = all_conferences.flat_map do |c|
        subs = c['sub']
        subs.is_a?(Array) ? subs : [subs.to_s]
      end.compact.uniq.sort

      # Generate one JSON page per subject
      all_subs.each do |sub|
        next if sub.empty?
        filtered = all_conferences.select do |c|
          subs = c['sub']
          subs.is_a?(Array) ? subs.include?(sub) : subs.to_s == sub
        end
        site.pages << SubjectJsonPage.new(site, site.source, sub, filtered)
      end
    end
  end
end
