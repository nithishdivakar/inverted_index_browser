document.addEventListener('DOMContentLoaded',async function() {
    const jsonData = await fetchData();

    // Vue.component('post', {
    //     props: ["uri", 'content', 'metadata'],
    //     template: `
    //     <div class="post" :id="uri">
    //         <big><b>[{{ '{{' }} metadata['index']{{ '}}' }}] {{ '{{' }} metadata['title'] {{ '}}' }}</b></big><br>
    //         <code>{{ '{{' }} uri {{ '}}' }}</code>
    //         <div v-html="content" class="post-content"></div>
    //         Tags:  <code v-for="tag in metadata['tags']"> #{{ '{{' }} tag {{ '}}' }}</code><br>
    //         ctime: {{ '{{' }} metadata['ctime'] {{ '}}' }}
    //     </div>
    //     `
    // });

    new Vue({
        el: '#app',
        data: {
	      	ii: jsonData,
	      	isDataLoaded: false,
            selectedTokens: [],
            tokenSearchQuery: ''
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
                let docsSet = new Set(); // Using a Set to store unique documents
                if (this.selectedTokens.length === 0) {
                    Object.values(this.ii.invertedIndex).flat().forEach(doc => docsSet.add(doc));
                } else {
                    let selectedDocs = new Set(this.ii.invertedIndex[this.selectedTokens[0]]);
					this.selectedTokens.forEach(token => {
						selectedDocs = this.set_intersect(selectedDocs, new Set(this.ii.invertedIndex[token]));
                    });
                    selectedDocs.forEach(doc_id => {
                        docsSet.add(doc_id);
                    });
                }

                let docs = Array.from(docsSet);

                // function splitDigitsAndAlphabets(str) {
                //   return str.match(/\d+|[a-zA-Z]+/g);
                // }

                // // Custom sort function for Zettelkasten IDs
                // function customZettelkastenSort(a, b) {
                //     const partsA = splitDigitsAndAlphabets(a);
                //     const partsB = splitDigitsAndAlphabets(b);

                //     for (let i = 0; i < Math.min(partsA.length, partsB.length); i++) {
                //         const partA = partsA[i];
                //         const partB = partsB[i];

                //         // Compare numbers
                //         if (!isNaN(partA) && !isNaN(partB)) {
                //             const numA = parseInt(partA, 10);
                //             const numB = parseInt(partB, 10);
                //             if (numA !== numB) {
                //                 return numA - numB;
                //             }
                //         } else if (partA !== partB) {
                //             return partA.localeCompare(partB);
                //         }
                //     }

                //   return partsA.length - partsB.length;
                // }

                // let D = docs.sort(customZettelkastenSort).map(doc => this.ii.documents[doc]).filter(Boolean);
                let D = docs.sort().map(doc => this.ii.documents[doc]).filter(Boolean);
                return D;
            },
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
            set_intersect(a,b){
	            let intersect = new Set([...a].filter(i => b.has(i)));
	            return intersect;
            }

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