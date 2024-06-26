document.addEventListener('DOMContentLoaded',async function() {
    const jsonData = await fetchData();
    new Vue({
        el: '#app',
        data: {
	      	ii: jsonData,
	      	isDataLoaded: false,
            selectedTokens: [],
            tokenSearchQuery: '',
            chronologicalSort: true,
            ORtokenSearch: false,
            showModal: false,
            newNoteContent: '',
            newNotePath: '',
	    },
        computed: {
            tokens() {
              	return Object.keys(this.ii.invertedIndex);
            },
            filteredTokens() {
                const query = this.tokenSearchQuery.toLowerCase();
                const matched_tokens = this.tokens.filter(token => {
                    const queryWords = query.toLowerCase().split(' ');
                    return queryWords.some(word => token.toLowerCase().includes(word));
                });
                return Array.from(new Set([...matched_tokens, ...this.selectedTokens])).sort(); 
            },
            displayedDocs() {
                let uniqueDocsSet = new Set(); // Using a Set to store unique documents

                if (this.selectedTokens.length === 0) {
                    // If no tokens are selected, add all documents from the inverted index
                    Object.values(this.ii.invertedIndex).flat().forEach(docId => uniqueDocsSet.add(docId));
                } else {
                    

                    // Initialize selectedDocs with the set of documents containing the first selected token
                    let selectedDocs = new Set(this.ii.invertedIndex[this.selectedTokens[0]]);

                    // Intersect sets of documents for each selected token
                    this.selectedTokens.forEach(token => {
                        if (this.ORtokenSearch){
                            selectedDocs = this.setUnion(selectedDocs, new Set(this.ii.invertedIndex[token]));
                        } else {
                            selectedDocs = this.setIntersect(selectedDocs, new Set(this.ii.invertedIndex[token]));
                        }
                    });

                    // Add the intersected document IDs to the uniqueDocsSet
                    selectedDocs.forEach(docId => uniqueDocsSet.add(docId));
                }

                // Convert the uniqueDocsSet to an array
                let uniqueDocsArray = Array.from(uniqueDocsSet);

                
                if(this.chronologicalSort){
                    let T = uniqueDocsArray.map(docId => this.ii.documents[docId]).filter(Boolean).sort(function(a,b){
                        // reverse
                        return b['metadata']['ctime'].localeCompare(a['metadata']['ctime']);
                    });
                    return T;

                } else {
                    let displayedDocuments = uniqueDocsArray.sort(this.customSortFn);
                    return displayedDocuments.map(docId => this.ii.documents[docId]).filter(Boolean);
                }  
            }
        },
        methods: {
            decodeBase64(b64string) {
                try{
                    return atob(b64string);
                } catch (error) {
                    console.error('Invalid Base64 string', error);
                    return "err"
                }
            },
            setIntersect(a,b){
	            let intersect = new Set([...a].filter(i => b.has(i)));
	            return intersect;
            },
            setUnion(a, b) {
                let union = new Set([...a, ...b]);
                return union;
            },
            customSortFn(a,b){
                // Zettelkasten Index Sort
                const partsA = String(a).match(/\d+|[a-zA-Z]+/g);
                const partsB = String(b).match(/\d+|[a-zA-Z]+/g);

                for (let i = 0; i < Math.min(partsA.length, partsB.length); i++) {
                    const partA = partsA[i];
                    const partB = partsB[i];

                    // Compare numbers
                    if (!isNaN(partA) && !isNaN(partB)) {
                        const numA = parseInt(partA, 10);
                        const numB = parseInt(partB, 10);
                        if (numA !== numB) {
                            return numA - numB;
                        }
                    } else if (partA !== partB) {
                        return partA.localeCompare(partB);
                    }
                }

                return partsA.length - partsB.length;
            },
            groupedTokens(tokens){
                // console.log(tokens);
                const grouped = {};
                for (const token of tokens){
                    const firstLetter = token.charAt(0).toUpperCase();
                    if(!(firstLetter in grouped)){
                        grouped[firstLetter] = [];
                    }
                    grouped[firstLetter].push(token);
                }

                // console.log(grouped);
                return grouped;
            },
            addNote() {
                const note = {
                    content: this.newNoteContent,
                    uri: this.newNotePath,
                };
                fetch('/api/add_note', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(note)
                })
                .then(response => response.json())
                .then(data => {
                    this.showModal = false;
                    this.ii.documents[data.uri] = data;
                });
            },
            async editNote(note_id) {
                console.log("editNote", note_id);
                if (typeof note_id === 'undefined') {
                    note_id = '_empty'
                    // this.newNoteContent = "";
                    // this.newNotePath = "";
                    // this.showModal = true;
                    console.log("empty");
                }
                    try {
                        const response = await fetch(`/api/get_note_content/${note_id}`);
                        const data = await response.json();
                        console.log(data);
                        this.newNoteContent = data.content;
                        this.newNotePath = data.note_id;
                        this.showModal = true;
                    } catch (error) {
                        console.error('Error fetching note content:', error);
                    }
                
            },
        }
    });
});

async function fetchData() {
	try {
		const response = await fetch('data.json');
		if (!response.ok) {
		 	throw new Error('Network response was not ok');
		}
		return await response.json();
	} catch (error) {
		console.error('Error loading JSON data:', error);
		return {};
	}
}