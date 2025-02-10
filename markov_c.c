#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_TRANSITION_STR_LEN 20000
#define MAX_WORD_LEN 10
#define ORDER 3
#define HASH_TABLE_SIZE 4096

typedef struct TransitionEntry {
	char state[ORDER + 1];
	char* transitions;
	struct TransitionEntry* next;
} TransitionEntry;

static TransitionEntry** transition_table = NULL;

unsigned int hash_state(const char* state) {
	unsigned int hash = 5381;
	for (int i = 0; i < ORDER; i++) {
		hash = ((hash << 5) + hash) + state[i];
	}
	return hash & (HASH_TABLE_SIZE - 1);
}

void init_transition_table() {
	transition_table = (TransitionEntry**)calloc(HASH_TABLE_SIZE, sizeof(TransitionEntry*));
	if (!transition_table) {
		PyErr_SetString(PyExc_MemoryError, "Failed to allocate transition table");
		return;
	}
}

void free_transition_table() {
	if (!transition_table)
		return;

	for (int i = 0; i < HASH_TABLE_SIZE; i++) {
		TransitionEntry* entry = transition_table[i];
		while (entry) {
			TransitionEntry* next = entry->next;
			free(entry->transitions);
			free(entry);
			entry = next;
		}
	}
	free(transition_table);
	transition_table = NULL;
}

void add_transition(const char* state, const char* trans) {
	unsigned int idx = hash_state(state);

	TransitionEntry* entry = transition_table[idx];
	while (entry) {
		if (strcmp(entry->state, state) == 0) {
			size_t current_len = strlen(entry->transitions);
			size_t new_len = strlen(trans);
			char* new_transitions = realloc(entry->transitions, current_len + new_len + 1);
			if (!new_transitions) {
				PyErr_SetString(PyExc_MemoryError, "Failed to reallocate transitions");
				return;
			}
			entry->transitions = new_transitions;
			strcat(entry->transitions, trans);
			return;
		}
		entry = entry->next;
	}

	entry = (TransitionEntry*)malloc(sizeof(TransitionEntry));
	if (!entry) {
		PyErr_SetString(PyExc_MemoryError, "Failed to allocate new entry");
		return;
	}

	strncpy(entry->state, state, ORDER);
	entry->state[ORDER] = '\0';
	entry->transitions = strdup(trans);
	if (!entry->transitions) {
		free(entry);
		PyErr_SetString(PyExc_MemoryError, "Failed to allocate transitions");
		return;
	}
	entry->next = transition_table[idx];
	transition_table[idx] = entry;
}

const char* get_transitions(const char* state) {
	unsigned int idx = hash_state(state);
	TransitionEntry* entry = transition_table[idx];

	while (entry) {
		if (strcmp(entry->state, state) == 0) {
			return entry->transitions;
		}
		entry = entry->next;
	}
	return NULL;
}

void generate_word(char* output) {
	memset(output, '^', ORDER);
	output[ORDER] = '\0';
	int len = ORDER;

	char state[ORDER + 1];
	while (len < MAX_WORD_LEN) {
		memcpy(state, output + len - ORDER, ORDER);
		state[ORDER] = '\0';

		const char* trans = get_transitions(state);
		if (!trans || !*trans)
			break;

		int tlen = strlen(trans);
		char next_char = trans[rand() % tlen];
		if (next_char == '$')
			break;

		output[len++] = next_char;
		output[len] = '\0';
	}

	memmove(output, output + ORDER, len - ORDER + 1);
}

// Python interface functions
static PyObject* load_transitions(PyObject* self, PyObject* args) {
	PyObject* states_list;
	PyObject* trans_list;

	if (!PyArg_ParseTuple(args, "OO", &states_list, &trans_list)) {
		return NULL;
	}

	if (!PyList_Check(states_list) || !PyList_Check(trans_list)) {
		PyErr_SetString(PyExc_TypeError, "Arguments must be lists");
		return NULL;
	}

	Py_ssize_t count = PyList_Size(states_list);
	if (count != PyList_Size(trans_list)) {
		PyErr_SetString(PyExc_ValueError, "Lists must have same length");
		return NULL;
	}

	free_transition_table();
	init_transition_table();
	srand((unsigned int)time(NULL));

	for (Py_ssize_t i = 0; i < count; i++) {
		PyObject* state = PyList_GetItem(states_list, i);
		PyObject* trans = PyList_GetItem(trans_list, i);

		const char* state_str = PyUnicode_AsUTF8(state);
		const char* trans_str = PyUnicode_AsUTF8(trans);

		if (!state_str || !trans_str) {
			free_transition_table();
			return NULL;
		}

		add_transition(state_str, trans_str);
	}

	Py_RETURN_NONE;
}

static PyObject* generate_single_word(PyObject* self, PyObject* args) {
	char word[MAX_WORD_LEN + 1];
	generate_word(word);
	return PyUnicode_FromString(word);
}

static PyObject* generate_multiple_words(PyObject* self, PyObject* args) {
	int count;
	if (!PyArg_ParseTuple(args, "i", &count)) {
		return NULL;
	}

	PyObject* result_list = PyList_New(count);
	if (!result_list)
		return NULL;

	for (int i = 0; i < count; i++) {
		char word[MAX_WORD_LEN + 1];
		generate_word(word);
		PyObject* word_str = PyUnicode_FromString(word);
		if (!word_str) {
			Py_DECREF(result_list);
			return NULL;
		}
		PyList_SET_ITEM(result_list, i, word_str);
	}

	return result_list;
}

static PyObject* cleanup(PyObject* self, PyObject* args) {
	free_transition_table();
	Py_RETURN_NONE;
}

static PyMethodDef MarkovMethods[] = {
	{"load_transitions", load_transitions, METH_VARARGS, "Load transition table"},
	{"generate_word", generate_single_word, METH_NOARGS, "Generate a single word"},
	{"generate_multiple_words", generate_multiple_words, METH_VARARGS, "Generate multiple words"},
	{"cleanup", cleanup, METH_NOARGS, "Clean up allocated memory"},
	{NULL, NULL, 0, NULL}};

static struct PyModuleDef markovmodule = {
	PyModuleDef_HEAD_INIT,
	"markov_c",
	"Markov chain word generator module",
	-1,
	MarkovMethods};

PyMODINIT_FUNC PyInit_markov_c(void) {
	return PyModule_Create(&markovmodule);
}