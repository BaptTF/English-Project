#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_TRANSITION_STR_LEN 20000  // Maximum length for one transition string.
#define MAX_WORD_LEN 10				  // Maximum total length of the generated word (including start tokens).
#define ORDER 3						  // Order of the Markov chain.

// --- Transition Table Structures and Functions ---

typedef struct {
	char state[ORDER + 1];					   // For example: "^^^", "^ab", "abc", etc.
	char transitions[MAX_TRANSITION_STR_LEN];  // Concatenated possible next characters.
} Transition;

// Global dynamic transition table.
static Transition* transition_table = NULL;
static int num_transitions = 0;
static int max_transitions = 0;

void init_transition_table(int initial_capacity) {
	max_transitions = initial_capacity;
	transition_table = (Transition*)malloc(sizeof(Transition) * max_transitions);
	if (!transition_table) {
		fprintf(stderr, "Memory allocation failed in init_transition_table\n");
		exit(1);
	}
	num_transitions = 0;
}

void free_transition_table() {
	if (transition_table) {
		free(transition_table);
		transition_table = NULL;
	}
	num_transitions = 0;
	max_transitions = 0;
}

// Add a transition entry. If the state already exists, append the new transitions.
void add_transition(const char* state, const char* trans) {
	// Check if this state already exists.
	for (int i = 0; i < num_transitions; i++) {
		if (strcmp(transition_table[i].state, state) == 0) {
			strncat(transition_table[i].transitions, trans,
					MAX_TRANSITION_STR_LEN - strlen(transition_table[i].transitions) - 1);
			return;
		}
	}
	// Expand table if needed.
	if (num_transitions >= max_transitions) {
		max_transitions = (max_transitions == 0) ? 10 : max_transitions * 2;
		Transition* new_table = (Transition*)realloc(transition_table, sizeof(Transition) * max_transitions);
		if (!new_table) {
			fprintf(stderr, "Memory reallocation failed in add_transition\n");
			exit(1);
		}
		transition_table = new_table;
	}
	// Add the new state.
	strncpy(transition_table[num_transitions].state, state, ORDER);
	transition_table[num_transitions].state[ORDER] = '\0';
	strncpy(transition_table[num_transitions].transitions, trans, MAX_TRANSITION_STR_LEN - 1);
	transition_table[num_transitions].transitions[MAX_TRANSITION_STR_LEN - 1] = '\0';
	num_transitions++;
}

// Retrieve the transition string for a given state.
const char* get_transitions(const char* state) {
	for (int i = 0; i < num_transitions; i++) {
		if (strcmp(transition_table[i].state, state) == 0) {
			return transition_table[i].transitions;
		}
	}
	return NULL;
}

/*
 * Exposed to Python: load transitions.
 * 'states' is an array of C strings representing the states.
 * 'trans'  is an array of C strings representing the corresponding transitions.
 * 'count' is the number of entries.
 */
void load_transitions_from_python(char** states, char** trans, int count) {
	int init_cap = (count > 10) ? count : 10;
	init_transition_table(init_cap);
	for (int i = 0; i < count; i++) {
		add_transition(states[i], trans[i]);
	}
	// Seed the random number generator.
	srand((unsigned int)time(NULL));
}

// --- Real Word Set Storage and Checking ---

// Global storage for the "real" word set.
static char** real_wordset = NULL;
static int real_wordset_size = 0;

/*
 * Exposed to Python: load the real word set.
 * 'words' is an array of C strings (the real words).
 * 'count' is the number of words.
 *
 * This function now duplicates each string with strdup so that the memory
 * remains valid even after the Python objects are freed.
 */
void load_wordset_from_python(char** words, int count) {
	// Free any previously loaded wordset.
	if (real_wordset) {
		for (int i = 0; i < real_wordset_size; i++) {
			free(real_wordset[i]);
		}
		free(real_wordset);
		real_wordset = NULL;
	}
	real_wordset_size = count;
	real_wordset = (char**)malloc(sizeof(char*) * count);
	if (!real_wordset) {
		fprintf(stderr, "Memory allocation failed in load_wordset_from_python\n");
		exit(1);
	}
	for (int i = 0; i < count; i++) {
		real_wordset[i] = strdup(words[i]);
		if (!real_wordset[i]) {
			fprintf(stderr, "Memory allocation failed in load_wordset_from_python (strdup)\n");
			exit(1);
		}
	}
}

// Helper function: Check if a word exists in the real word set.
// Returns 1 if found, 0 otherwise.
int word_exists(const char* word) {
	if (real_wordset == NULL)
		return 0;
	for (int i = 0; i < real_wordset_size; i++) {
		if (strcmp(word, real_wordset[i]) == 0) {
			return 1;
		}
	}
	return 0;
}

// --- Word Generation Functions ---

/*
 * Basic word generation function.
 * 'output' should point to a buffer of at least MAX_WORD_LEN+1 bytes.
 *
 * The function starts by writing ORDER '^' characters (start tokens),
 * then it appends characters based on the transition table until either
 * the special end marker '$' is reached or MAX_WORD_LEN is hit.
 * Finally, it removes the initial ORDER '^' tokens.
 */
void generate_word(char* output) {
	// Initialize with ORDER start tokens.
	for (int i = 0; i < ORDER; i++) {
		output[i] = '^';
	}
	output[ORDER] = '\0';
	int len = ORDER;

	while (len < MAX_WORD_LEN) {
		// Copy the last ORDER characters as the current state.
		char state[ORDER + 1];
		memcpy(state, output + len - ORDER, ORDER);
		state[ORDER] = '\0';

		const char* trans = get_transitions(state);
		if (trans == NULL)
			break;
		int tlen = (int)strlen(trans);
		if (tlen == 0)
			break;
		// Choose a random character from the transitions.
		int idx = rand() % tlen;
		char next_char = trans[idx];
		if (next_char == '$')
			break;
		output[len] = next_char;
		len++;
		output[len] = '\0';
	}
	// Remove the initial ORDER '^' tokens.
	int final_len = len - ORDER;
	memmove(output, output + ORDER, final_len + 1);
}

/*
 * Extended word generation: generate a word that is not in the real word set.
 * 'output' should point to a buffer of at least MAX_WORD_LEN+1 bytes.
 *
 * This function repeatedly calls generate_word() until it produces a word that
 * is not found in the real word set or until a maximum number of tries is reached.
 */
void generate_fake_word(char* output) {
	int tries = 0;
	// Try up to 100 times to avoid an infinite loop.
	do {
		generate_word(output);
		tries++;
	} while (word_exists(output) && tries < 100);
}

// New function to generate multiple fake words in one call.
// words: preallocated array of char pointers (each word buffer should be at least MAX_WORD_LEN+1 bytes).
// count: number of words to generate.
void generate_multiple_fake_words(char** words, int count) {
	for (int i = 0; i < count; i++) {
		// Each words[i] should be a preallocated buffer.
		generate_fake_word(words[i]);
	}
}
