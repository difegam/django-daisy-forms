/*
 * django-daisy-forms: opt-in add and remove controls for formsets rendered
 * with daisy_forms/formset_dynamic.html or daisy_forms/formset_table.html.
 * Without this script those templates still submit, using the DELETE checkbox.
 */
(() => {
  "use strict";

  const FORMSET = "[data-daisy-formset]";
  const FORM = "[data-daisy-formset-form]";
  const FOCUSABLE =
    "input:not([type=hidden]):not([disabled]), select:not([disabled]), textarea:not([disabled])";
  const VALIDATION_CONTROLS = "input:not([type=hidden]), select, textarea";
  const RENUMBERED = ["id", "name", "for", "aria-describedby", "aria-labelledby"];

  const escapeRegExp = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  function setup(container) {
    if (container.dataset.daisyFormsetReady) return;
    container.dataset.daisyFormsetReady = "true";

    const prefix = container.dataset.prefix;
    const labels = container.dataset;
    const owns = (element, scope) => element.closest(scope) === container;
    const own = (selector) =>
      Array.from(container.querySelectorAll(selector)).find((element) =>
        owns(element, FORMSET),
      );
    const management = (name) => own(`input[name="${prefix}-${name}"]`);
    const total = management("TOTAL_FORMS");
    const initial = management("INITIAL_FORMS");
    const minimum = management("MIN_NUM_FORMS");
    const maximum = management("MAX_NUM_FORMS");
    const list = own("[data-daisy-formset-forms]");
    const template = own("template[data-daisy-formset-template]");
    const addButton = own("[data-daisy-formset-add]");
    const status = own("[data-daisy-formset-status]");
    if (!total || !initial || !list || !template) return;

    const deletePattern = new RegExp(`^${escapeRegExp(prefix)}-\\d+-DELETE$`);
    const indexPattern = new RegExp(`(${escapeRegExp(prefix)}-)\\d+(-)`, "g");
    const disabledStates = new WeakMap();

    const rows = () =>
      Array.from(list.children).filter((element) => element.matches(FORM));
    const inRow = (row, selector) =>
      Array.from(row.querySelectorAll(selector)).filter(
        (element) => element.closest(FORM) === row,
      );
    const deleteInput = (row) =>
      inRow(row, 'input[type="checkbox"]').find((input) =>
        deletePattern.test(input.name),
      );
    const removeButton = (row) => inRow(row, "[data-daisy-formset-remove]")[0];
    const isDeleted = (row) => row.hasAttribute("data-deleted");
    const isSaved = (row) => rows().indexOf(row) < Number(initial.value);

    function announce(message) {
      if (!status || !message) return;
      status.textContent = "";
      requestAnimationFrame(() => {
        status.textContent = message;
      });
    }

    function markDeleted(row, deleted) {
      const input = deleteInput(row);
      if (input) input.checked = deleted;
      row.toggleAttribute("data-deleted", deleted);
      for (const control of inRow(row, VALIDATION_CONTROLS)) {
        if (control === input) continue;
        if (deleted) {
          if (!disabledStates.has(control)) {
            disabledStates.set(control, control.disabled);
          }
          control.disabled = true;
        } else if (disabledStates.has(control)) {
          control.disabled = disabledStates.get(control);
          disabledStates.delete(control);
        }
      }
      for (const body of inRow(row, "[data-daisy-formset-body]")) {
        body.inert = deleted;
        body.classList.toggle("opacity-50", deleted);
      }
    }

    function prepare(row) {
      const input = deleteInput(row);
      if (!input) return;
      const wrapper =
        input.closest("[data-daisy-formset-delete]") || input.closest(".fieldset");
      if (wrapper && wrapper.closest(FORM) === row) wrapper.hidden = true;
      if (input.checked) markDeleted(row, true);
    }

    function refresh() {
      const all = rows();
      const active = all.filter((row) => !isDeleted(row)).length;
      const min = Number(minimum ? minimum.value : 0);
      const max = Number(maximum ? maximum.value : Infinity);
      all.forEach((row, index) => {
        const button = removeButton(row);
        if (!button) return;
        const saved = index < Number(initial.value);
        button.hidden = saved && !deleteInput(row);
        const label = isDeleted(row) ? labels.undoLabel : labels.removeLabel;
        button.textContent = label;
        button.setAttribute("aria-label", `${label} ${index + 1}`);
        button.disabled = isDeleted(row) ? active >= max : active <= min;
      });
      if (addButton) {
        addButton.hidden = false;
        addButton.disabled = active >= max;
      }
    }

    function renumber(row, index) {
      for (const element of [row, ...row.querySelectorAll("*")]) {
        for (const name of RENUMBERED) {
          const value = element.getAttribute(name);
          if (value) {
            element.setAttribute(name, value.replace(indexPattern, `$1${index}$2`));
          }
        }
      }
    }

    function focusFirst(...candidates) {
      const target = candidates.find(
        (element) => element && !element.hidden && !element.disabled,
      );
      if (target) target.focus();
    }

    function add() {
      const index = Number(total.value);
      const fragment = document.createElement("template");
      fragment.innerHTML = template.innerHTML.replace(/__prefix__/g, String(index));
      const row = fragment.content.firstElementChild;
      if (!row) return;
      list.append(row);
      total.value = String(index + 1);
      prepare(row);
      refresh();
      focusFirst(row.querySelector(FOCUSABLE), removeButton(row));
      announce(labels.addedMessage);
      init(row);
      if (window.htmx) window.htmx.process(row);
      row.dispatchEvent(
        new CustomEvent("daisy-formset:added", { bubbles: true, detail: { index } }),
      );
    }

    function remove(row) {
      const button = removeButton(row);
      if (isSaved(row)) {
        const deleted = !isDeleted(row);
        markDeleted(row, deleted);
        refresh();
        announce(deleted ? labels.removedMessage : labels.restoredMessage);
        focusFirst(button, addButton);
        return;
      }
      const all = rows();
      const index = all.indexOf(row);
      const next = all[index + 1];
      row.remove();
      rows()
        .slice(index)
        .forEach((later, offset) => renumber(later, index + offset));
      total.value = String(rows().length);
      refresh();
      announce(labels.removedMessage);
      focusFirst(next && removeButton(next), addButton);
      container.dispatchEvent(
        new CustomEvent("daisy-formset:removed", { bubbles: true, detail: { index } }),
      );
    }

    container.addEventListener("click", (event) => {
      const button = event.target.closest(
        "[data-daisy-formset-add], [data-daisy-formset-remove]",
      );
      if (!button || !owns(button, FORMSET)) return;
      if (button.matches("[data-daisy-formset-add]")) {
        add();
      } else {
        const row = button.closest(FORM);
        if (row) remove(row);
      }
    });

    const form = container.closest("form");
    if (form) {
      form.addEventListener("submit", () => {
        const controls = rows().filter(isDeleted).flatMap((row) =>
          inRow(row, VALIDATION_CONTROLS).filter(
            (control) => disabledStates.has(control) && !disabledStates.get(control),
          ),
        );
        controls.forEach((control) => {
          control.disabled = false;
        });
        setTimeout(() => {
          controls.forEach((control) => {
            const row = control.closest(FORM);
            if (row && isDeleted(row)) control.disabled = true;
          });
        }, 0);
      }, true);
    }

    rows().forEach(prepare);
    refresh();
  }

  function init(root = document) {
    const containers = root.matches && root.matches(FORMSET) ? [root] : [];
    containers.push(...root.querySelectorAll(FORMSET));
    containers.forEach(setup);
  }

  window.daisyForms = Object.assign(window.daisyForms || {}, { initFormsets: init });
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => init());
  } else {
    init();
  }
  document.addEventListener("htmx:load", (event) => init(event.target));
})();
