-- Config Neovim propre au dossier story.
-- Chargée automatiquement si `vim.o.exrc = true` dans ta config, sinon : nvim -S .nvim.lua _index.md

local root = vim.fn.fnamemodify(debug.getinfo(1, "S").source:sub(2), ":p:h")
vim.cmd.cd(root)

local grp = vim.api.nvim_create_augroup("story", { clear = true })

-- Écriture : lignes longues coupées à l'écran, sans couper les mots
vim.api.nvim_create_autocmd("FileType", {
  group = grp,
  pattern = "markdown",
  callback = function()
    vim.opt_local.wrap = true
    vim.opt_local.linebreak = true
    vim.opt_local.breakindent = true
    vim.opt_local.conceallevel = 0
    -- Entrée : ouvre le passage cité sur la ligne (lignes → et _index.md)
    vim.keymap.set("n", "<CR>", function()
      local f = vim.api.nvim_get_current_line():match("scripts/[%w%-]+%.md")
      if f then vim.cmd.edit(root .. "/" .. f) end
    end, { buffer = true, desc = "Ouvrir le passage" })
    -- Retour arrière : revient au fichier précédent
    vim.keymap.set("n", "<BS>", "<C-o>", { buffer = true, desc = "Revenir" })
  end,
})

-- À l'ouverture d'un passage, curseur directement sous "## Texte"
vim.api.nvim_create_autocmd("BufReadPost", {
  group = grp,
  pattern = "*/scripts/*.md",
  callback = function()
    local line = vim.fn.search("^## Texte", "nw")
    if line > 0 then
      vim.api.nvim_win_set_cursor(0, { math.min(line + 2, vim.fn.line("$")), 0 })
    end
  end,
})

local function py()
  return vim.fn.executable("python3") == 1 and "python3" or "python"
end

-- Reconstruit _index.md en arrière-plan puis recharge le buffer
local function rebuild_index()
  vim.fn.jobstart({ py(), root .. "/index.py" }, {
    on_exit = function() vim.schedule(function() vim.cmd("checktime") end) end,
  })
end
vim.o.autoread = true

-- Après chaque sauvegarde d'un passage, l'index suit les nouveaux liens
vim.api.nvim_create_autocmd("BufWritePost", {
  group = grp,
  pattern = "*/scripts/*.md",
  callback = rebuild_index,
})

-- Dans _index.md : branches pliables et <leader>x coche / décoche (et enregistre)
vim.api.nvim_create_autocmd("BufEnter", {
  group = grp,
  pattern = "*/_index.md",
  callback = function()
    vim.opt_local.wrap = false
    vim.opt_local.foldmethod = "indent"
    vim.opt_local.shiftwidth = 2
    if not vim.b.story_folds then
      vim.opt_local.foldlevel = 99
      vim.b.story_folds = true
    end
    vim.keymap.set("n", "<leader>x", function()
      local l = vim.api.nvim_get_current_line()
      if l:find("^%s*%- %[ %]") then
        l = l:gsub("%- %[ %]", "- [x]", 1)
      elseif l:find("^%s*%- %[x%]") then
        l = l:gsub("%- %[x%]", "- [ ]", 1)
      end
      vim.api.nvim_set_current_line(l)
      vim.cmd("silent write")
    end, { buffer = true, desc = "Cocher le passage" })
  end,
})

-- :Index reconstruit et ouvre la liste, :Build crée export.twee
vim.api.nvim_create_user_command("Index", function()
  vim.cmd("silent !" .. py() .. " " .. vim.fn.shellescape(root .. "/index.py"))
  vim.cmd("edit! " .. root .. "/_index.md")
end, {})
vim.api.nvim_create_user_command("Build", function()
  vim.cmd("wall")
  vim.cmd("!" .. py() .. " " .. vim.fn.shellescape(root .. "/build.py"))
end, {})

-- Avec `nvim -S`, le premier fichier est déjà ouvert : on lui applique aussi la config
for _, b in ipairs(vim.api.nvim_list_bufs()) do
  if vim.api.nvim_buf_is_loaded(b) and vim.bo[b].filetype == "markdown" then
    vim.api.nvim_buf_call(b, function() vim.cmd("doautocmd story FileType markdown") end)
  end
end
vim.cmd("doautocmd story BufEnter")
