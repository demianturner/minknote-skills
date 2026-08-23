#!/usr/bin/env node

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");
const skillsRoot = path.join(repoRoot, "skills");

const usage = `Usage:
  minknote-skills list
  minknote-skills install <skill|all> [--agent codex|cursor] [--dest <path>] [--force]

Examples:
  npx github:demianturner/minknote-skills list
  npx github:demianturner/minknote-skills install minknote-docs-import --agent codex
  npx github:demianturner/minknote-skills install all --dest .cursor/skills --force
`;

function fail(message) {
  console.error(message);
  process.exit(1);
}

function parseArgs(argv) {
  const [command, target, ...rest] = argv;
  const options = {
    agent: "codex",
    dest: null,
    force: false,
  };

  for (let index = 0; index < rest.length; index += 1) {
    const arg = rest[index];
    if (arg === "--force") {
      options.force = true;
    } else if (arg === "--agent") {
      options.agent = rest[index + 1];
      index += 1;
    } else if (arg === "--dest") {
      options.dest = rest[index + 1];
      index += 1;
    } else if (arg === "--help" || arg === "-h") {
      options.help = true;
    } else {
      fail(`Unknown option: ${arg}\n\n${usage}`);
    }
  }

  return { command, target, options };
}

function availableSkills() {
  return fs
    .readdirSync(skillsRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
}

function destinationFor(options) {
  if (options.dest) {
    return path.resolve(options.dest);
  }

  if (options.agent === "codex") {
    return path.join(os.homedir(), ".codex", "skills");
  }

  if (options.agent === "cursor") {
    return path.resolve(".cursor", "skills");
  }

  fail(`Unsupported agent: ${options.agent}`);
}

function copyDirectory(source, destination, force) {
  if (fs.existsSync(destination)) {
    if (!force) {
      fail(`Destination already exists: ${destination}\nPass --force to replace it.`);
    }
    fs.rmSync(destination, { recursive: true, force: true });
  }

  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.cpSync(source, destination, {
    recursive: true,
    filter: (src) => !src.includes(`${path.sep}.DS_Store`),
  });
}

function install(target, options) {
  if (!target) {
    fail(`Missing skill name.\n\n${usage}`);
  }

  const skills = availableSkills();
  const selected = target === "all" ? skills : [target];
  const unknown = selected.filter((skill) => !skills.includes(skill));
  if (unknown.length > 0) {
    fail(`Unknown skill: ${unknown.join(", ")}\nAvailable skills: ${skills.join(", ")}`);
  }

  const destRoot = destinationFor(options);
  for (const skill of selected) {
    copyDirectory(path.join(skillsRoot, skill), path.join(destRoot, skill), options.force);
    console.log(`Installed ${skill} -> ${path.join(destRoot, skill)}`);
  }
}

const { command, target, options } = parseArgs(process.argv.slice(2));

if (options.help || command === "--help" || command === "-h" || !command) {
  console.log(usage);
} else if (command === "list") {
  for (const skill of availableSkills()) {
    console.log(skill);
  }
} else if (command === "install") {
  install(target, options);
} else {
  fail(`Unknown command: ${command}\n\n${usage}`);
}
