#!/usr/bin/env ruby
require 'fileutils'
require 'json'

SETTINGS_FILENAME = ".claude/settings.json"
DEFAULT_SETTINGS = {
  permissions: {
    allow: [],
    deny: ["Read(.env)", "Read(.env.shared)"]
  }
}
ADDITIONS = [
  "Bash(hokusai:*)",
  "Bash(aws:*)"
]

# create settings file if it doesn't already exist
unless File.exist?(SETTINGS_FILENAME)
  FileUtils.mkdir_p(".claude")
  File.open(SETTINGS_FILENAME, 'w') do |f|
    f.write(JSON.pretty_generate(DEFAULT_SETTINGS))
  end
end

# read in settings
settings = JSON.parse(File.read(SETTINGS_FILENAME))

# remove typos (e.g.)...
# settings["permissions"]["deny"] -= ["Bash(aws:*)]"]

# merge additions
settings["permissions"]["deny"] |= ADDITIONS

# write out updated settings
File.open(SETTINGS_FILENAME, 'w') do |f|
  f.write(JSON.pretty_generate(settings))
end

