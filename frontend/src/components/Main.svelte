<script lang="ts">
  import { parseCSV } from "../lib/csv";
  import { writable, derived, get } from "svelte/store";
  import { sender } from "../singletons";

  const column_names = writable([]);
  const contacts = writable([]);

  let name_column = $state("");
  let phone_column = $state("");
  const name_column_id = writable();
  const phone_column_id = writable();
  $effect(() => {
    const names = get(column_names);
    name_column_id.set(names.indexOf(name_column));
    phone_column_id.set(names.indexOf(phone_column));
  });

  const valid_contacts = derived(
    [contacts, name_column_id, phone_column_id],
    ([rows, name, phone]) =>
      rows.filter((row) => isValid(row[name]) && isValid(row[phone])),
  );
  function isValid(value?: string) {
    return value !== undefined && value !== "";
  }
  const n_contacts = derived(valid_contacts, (rows) => rows.length);

  let user_message = $state("Ciao {nome}!");

  function onFileInputChange(e: Event) {
    const file = (e.target as HTMLInputElement).files[0];
    reader.readAsText(file);
  }

  const reader = new FileReader();
  reader.onload = (e: Event) => {
    const content = e.target.result as string;
    const { columns, data } = parseCSV(content);
    column_names.set(columns);
    contacts.set(data);
  };

  function sendMessages() {
    const messages = getMessages();
    return sender.sendMessages(messages);
  }

  function sendMessagesDry() {
    const messages = getMessages();
    return sender.sendMessages(messages, { dry: true });
  }

  function getMessages() {
    const phone = get(phone_column_id);
    const name = get(name_column_id);
    return get(valid_contacts).map((row) => {
      return {
        phone: row[phone],
        message: user_message.replaceAll("{nome}", formatName(row[name])),
      };
    });
  }

  function formatName(name: string) {
    return (
      String(name).charAt(0).toUpperCase() + String(name).slice(1).toLowerCase()
    );
  }
</script>

<div>
  <label>
    Seleziona il file CSV con i contatti:<br />
    <input type="file" accept=".csv" onchange={onFileInputChange} /><br />
  </label><br />
  <label>
    Seleziona la colonna con i nomi dei contatti:<br />
    <select id="column-name" bind:value={name_column}>
      {#each $column_names as column}
        <option value={column}>{column}</option>
      {/each}
    </select><br />
  </label><br />
  <label>
    Seleziona la colonna con il numero di telefono dei contatti:<br />
    <select id="column-phone" bind:value={phone_column}>
      {#each $column_names as column}
        <option value={column}>{column}</option>
      {/each}
    </select><br />
  </label><br />
  <label>
    Numero di contatti validi:<br />
    <input value={$n_contacts} disabled /><br />
  </label><br />
  <label>
    Scrivi il tuo messaggio.<br />
    Per inserire il nome della persona, usa questo placeholder: {"{"}nome{"}"}<br
    />
    <textarea bind:value={user_message}></textarea><br />
  </label><br />
  <label>
    <button onclick={sendMessages}>Invia i messaggi</button><br />
  </label><br />
  <label>
    <button onclick={sendMessagesDry}>Invia i messaggi (Dry Mode)</button><br />
  </label>
</div>
