#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <math.h>


int main(void)
{
    // Get input text from user
    string user_text = get_string("Text: ");
    
    int letters = 0;
    int words = 0;
    int sentences = 0;
    int n = strlen(user_text);
    
    if (n > 0)
    {
        words = 1;
        // Changing characters from user text to ASCII code numbers and computing number of letters, words, sentences
        for (int i = 0; i < n; i++)
        {
            int c = (int) user_text[i];
            // Checking if character = "A-Z" or "a-z" in ASCII table
            if (((c >= 65) && (c <= 90)) || ((c >= 97) && (c <= 122)))
            {
                letters++;
            }
            // Checking if character = "space"
            else if (c == 32)
            {
                words++;
            }
            // Checking if character = "!" or "." or "?"
            else if ((c == 33) || (c == 46) || (c == 63))
            {
                sentences++;
            }
            
        }   
    }
    
    // Computing Coleman-Liau index
    float L = (letters * 100.00 / words);
    float S = (sentences * 100.00 / words);
    float index = (0.0588 * L) - (0.296 * S) - 15.8;
    int grade = round(index);
    
    
    // Final resolt
    if (index >= 16)
    {
        printf("Grade 16+\n");
    }
    else if (index < 1)
    {
        printf("Before Grade 1\n");
    }
    else
    {
        printf("%i letter(s)\n", letters);
        printf("%i word(s)\n", words);
        printf("%i sentence(s)\n", sentences);
        printf("Grade %i\n", grade);
    }
}

